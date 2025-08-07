import os, json
import logging
import logging.config
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from datetime import datetime
from config import Config
from auth import login_required, authenticate, add_user, get_user_role
from crypto_utils import (
    generate_root, sign_csr, load_root_cert, build_crl, load_issued_metadata
)

def create_app():
    # Setup Flask
    app = Flask(__name__)
    app.config.from_object(Config)

    # Setup logging
    if os.path.exists("logging.conf"):
        logging.config.fileConfig('logging.conf')
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Ensure required directories
    os.makedirs(app.config['DATA_PATH'], exist_ok=True)
    os.makedirs(os.path.join(app.config['DATA_PATH'], 'issued'), exist_ok=True)

    # Initialize Root CA if not present
    if not os.path.exists(os.path.join(app.config['DATA_PATH'], 'root_cert.pem')):
        logger.info("Bootstrapping Root CA")
        generate_root()

    # Routes
    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            u = request.form.get('username')
            p = request.form.get('password')
            if authenticate(u, p):
                session['username'] = u
                flash('Logged in', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required()
    def dashboard():
        issued = load_issued_metadata(app.config['DATA_PATH'])
        role = get_user_role(session['username'])
        return render_template('dashboard.html', issued=issued, role=role)

    @app.route('/submit', methods=['GET','POST'])
    @login_required(role='requester')
    def submit_csr():
        if request.method == 'POST':
            uploaded = request.files.get('csr')
            if not uploaded:
                flash('No file', 'danger')
                return redirect(request.url)
            try:
                csr_pem = uploaded.read()
                cert, serial = sign_csr(csr_pem, session['username'])
                logger.info(f"Cert issued serial={serial} requester={session['username']}")
                flash(f"Certificate issued, serial {serial}", 'success')
            except Exception as e:
                logger.error("CSR sign failed", exc_info=e)
                flash(str(e), 'danger')
            return redirect(url_for('dashboard'))
        return render_template('submit_csr.html')

    @app.route('/revoke/<int:serial>', methods=['POST'])
    @login_required(role='admin')
    def revoke(serial):
        try:
            issued = load_issued_metadata(app.config['DATA_PATH'])
            target = next((m for m in issued if m['serial'] == serial), None)
            if not target:
                flash('Not found', 'danger')
            else:
                target['revoked'] = True
                target['revoked_at'] = datetime.utcnow().isoformat()
                with open(os.path.join(app.config['DATA_PATH'],'issued',f'{serial}.json'), 'w') as f:
                    json.dump(target, f)
                build_crl([m for m in issued if m.get('revoked')])
                logger.warning(f"Certificate revoked serial={serial}")
                flash(f"Revoked cert {serial}", 'warning')
        except Exception as e:
            logger.error("Revocation error", exc_info=e)
            flash('Error revoking', 'danger')
        return redirect(url_for('dashboard'))

    @app.route('/download/cert/<int:serial>')
    @login_required()
    def download_cert(serial):
        path = os.path.join(app.config['DATA_PATH'], 'issued', f'{serial}.crt')
        if not os.path.exists(path): 
            return render_template('error.html', message="Cert not found"), 404
        return send_file(path, as_attachment=True)

    @app.route('/download/crl')
    @login_required()
    def download_crl():
        crl = os.path.join(app.config['DATA_PATH'], 'crl.pem')
        if not os.path.exists(crl):
            return render_template('error.html', message="CRL missing"), 404
        return send_file(crl, as_attachment=True)

    @app.route('/root_cert.pem')
    def public_root_cert():
        return send_file(os.path.join(app.config['DATA_PATH'], 'root_cert.pem'))

    # API endpoints
    @app.route('/api/sign', methods=['POST'])
    @login_required(role='requester')
    def api_sign():
        csr_pem = request.data
        try:
            cert, serial = sign_csr(csr_pem, session['username'])
            logger.info(f"API sign serial={serial} requester={session['username']}")
            return jsonify(serial=serial, certificate=cert.public_bytes().decode()), 201
        except Exception as e:
            logger.error("API signing error", exc_info=e)
            return jsonify(error=str(e)), 400

    @app.route('/api/crl', methods=['GET'])
    @login_required()
    def api_crl():
        return send_file(os.path.join(app.config['DATA_PATH'], 'crl.pem'))

    @app.errorhandler(500)
    def handle_500(e):
        logger.error("Server error", exc_info=e)
        return render_template('error.html', message="Server error"), 500

    return app

# Expose app object for gunicorn
app = create_app()

# Only for Flask CLI/local dev
if __name__ == '__main__':
    if Config.TLS_CERT and Config.TLS_KEY:
        app.run(host='0.0.0.0', port=443, ssl_context=(Config.TLS_CERT, Config.TLS_KEY))
    else:
        app.run(host='0.0.0.0', port=8080)

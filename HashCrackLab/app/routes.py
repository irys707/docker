import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
from app.utils import allowed_hash_file, allowed_wordlist_file, detect_hash_mode
from app.hashcat_runner import run_hashcat, parse_results

bp = Blueprint('routes', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['job_id'] = str(uuid.uuid4())
        text_hashes = request.form.get('hashes')
        hash_file = request.files.get('hashfile')

        upload_path = None
        if hash_file and allowed_hash_file(hash_file.filename):
            filename = secure_filename(hash_file.filename)
            upload_path = os.path.join('app/uploads', f"{session['job_id']}_{filename}")
            hash_file.save(upload_path)
        elif text_hashes:
            upload_path = os.path.join('app/uploads', f"{session['job_id']}_input.txt")
            with open(upload_path, 'w') as f:
                f.write(text_hashes.strip())

        if not upload_path:
            flash("No valid hash input provided.")
            return redirect(url_for('routes.index'))

        session['hash_path'] = upload_path
        return redirect(url_for('routes.configure'))

    return render_template('index.html')


@bp.route('/configure', methods=['GET', 'POST'])
def configure():
    wordlists = os.listdir('app/wordlists')

    if request.method == 'POST':
        selected_wordlist = request.form.get('wordlist')
        uploaded_wordlist = request.files.get('custom_wordlist')

        if uploaded_wordlist and allowed_wordlist_file(uploaded_wordlist.filename):
            filename = secure_filename(uploaded_wordlist.filename)
            wordlist_path = os.path.join('app/wordlists', f"{session['job_id']}_{filename}")
            uploaded_wordlist.save(wordlist_path)
        elif selected_wordlist:
            wordlist_path = os.path.join('app/wordlists', selected_wordlist)
        else:
            flash("No wordlist selected or uploaded.")
            return redirect(url_for('routes.configure'))

        hash_mode = detect_hash_mode(session['hash_path'])
        session['wordlist_path'] = wordlist_path
        session['hash_mode'] = hash_mode

        return redirect(url_for('routes.crack'))

    return render_template('configure.html', wordlists=wordlists)


@bp.route('/crack')
def crack():
    result_path = run_hashcat(
        hash_file=session['hash_path'],
        wordlist=session['wordlist_path'],
        mode=session['hash_mode'],
        job_id=session['job_id']
    )
    session['result_path'] = result_path
    return redirect(url_for('routes.results'))


@bp.route('/results')
def results():
    results = parse_results(session.get('result_path'))
    return render_template('results.html', results=results)


@bp.route('/download')
def download():
    return send_file(session.get('result_path'), as_attachment=True)

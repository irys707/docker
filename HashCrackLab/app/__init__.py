import os
from flask import Flask
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'app/uploads'
WORDLIST_FOLDER = 'app/wordlists'
RESULTS_FOLDER = 'app/cracked_results'
JOBS_FOLDER = 'app/jobs'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET", "supersecret")
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['WORDLIST_FOLDER'] = WORDLIST_FOLDER
    app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
    app.config['JOBS_FOLDER'] = JOBS_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    from app.routes import bp
    app.register_blueprint(bp)

    for folder in [UPLOAD_FOLDER, WORDLIST_FOLDER, RESULTS_FOLDER, JOBS_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    return app

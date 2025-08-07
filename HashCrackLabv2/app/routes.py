from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from app.fuzzgen import generate_fuzz_wordlist
from app.hashcat import run_hashcat
from app.utils import detect_hash_type
import os, uuid, json

main = Blueprint('main', __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session['hashes'] = request.form.get("hashes") or request.files.get("hash_file").read().decode()
        session['hash_type'] = request.form.get("hash_type") or detect_hash_type(session['hashes'])
        return redirect(url_for("main.select_mode"))
    return render_template("index.html")

@main.route("/select-mode", methods=["GET", "POST"])
def select_mode():
    if request.method == "POST":
        session['mode'] = request.form.get("mode")
        return redirect(url_for("main.crack"))
    return render_template("select_mode.html")

@main.route("/crack", methods=["GET", "POST"])
def crack():
    wordlist_path = ""
    if session['mode'] == "auto":
        wordlist_path = generate_fuzz_wordlist()
    else:
        file = request.files.get("custom_wordlist")
        wordlist_path = os.path.join("app", "storage", "uploads", file.filename)
        file.save(wordlist_path)

    result_id = str(uuid.uuid4())
    result_file = run_hashcat(session['hashes'], session['hash_type'], wordlist_path, result_id)
    session['result_file'] = result_file

    return redirect(url_for("main.results"))

@main.route("/results")
def results():
    result_path = session.get("result_file")
    with open(result_path) as f:
        cracked = json.load(f)
    return render_template("results.html", results=cracked)

@main.route("/download")
def download():
    return send_file(session.get("result_file"), as_attachment=True)

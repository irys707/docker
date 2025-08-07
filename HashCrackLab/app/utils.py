import re
import os

def allowed_hash_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt']

def allowed_wordlist_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['txt', 'lst']

def detect_hash_mode(file_path):
    with open(file_path) as f:
        first_line = f.readline().strip()
        if re.fullmatch(r"[a-fA-F\d]{32}", first_line):
            return '0'  # MD5
        elif re.fullmatch(r"[a-fA-F\d]{40}", first_line):
            return '100'  # SHA1
        elif re.fullmatch(r"[a-fA-F\d]{32}:[a-fA-F\d]{32}", first_line):
            return '3000'  # NTLM
        else:
            return '0'  # fallback to MD5

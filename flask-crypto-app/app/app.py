from flask import Blueprint, render_template, request
from .crypto_utils import *

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    error = ''
    if request.method == 'POST':
        method = request.form.get('method')
        text = request.form.get('text')
        key = request.form.get('key', '')

        try:
            if method == 'caesar_encrypt':
                result = caesar_cipher(text)
            elif method == 'caesar_decrypt':
                result = caesar_cipher(text, decrypt=True)
            elif method == 'base64_encode':
                result = base64_encode(text)
            elif method == 'base64_decode':
                result = base64_decode(text)
            elif method == 'aes_encrypt':
                result = aes_encrypt(text, key)
            elif method == 'aes_decrypt':
                result = aes_decrypt(text, key)
        except Exception as e:
            error = str(e)

    return render_template('index.html', result=result, error=error, key=generate_key())

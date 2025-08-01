import base64
from cryptography.fernet import Fernet

def caesar_cipher(text, shift=3, decrypt=False):
    if decrypt:
        shift = -shift
    return ''.join(
        chr((ord(char) - 65 + shift) % 26 + 65) if char.isupper() else
        chr((ord(char) - 97 + shift) % 26 + 97) if char.islower() else char
        for char in text
    )

def base64_encode(text):
    return base64.b64encode(text.encode()).decode()

def base64_decode(text):
    return base64.b64decode(text.encode()).decode()

def generate_key():
    return Fernet.generate_key().decode()

def aes_encrypt(text, key):
    return Fernet(key.encode()).encrypt(text.encode()).decode()

def aes_decrypt(token, key):
    return Fernet(key.encode()).decrypt(token.encode()).decode()

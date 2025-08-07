import os

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'please-change')
    DATA_PATH = os.getenv('DATA_PATH', '/data/ca')
    CA_LIFETIME_DAYS = int(os.getenv('CA_LIFETIME_DAYS', '3650'))
    CERT_LIFETIME_DAYS = int(os.getenv('CERT_LIFETIME_DAYS', '365'))
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASS = os.getenv('ADMIN_PASS', 'adminpass')
    TLS_CERT = os.getenv('TLS_CERT')
    TLS_KEY = os.getenv('TLS_KEY')

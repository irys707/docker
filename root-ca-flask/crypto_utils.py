import os, json
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from config import Config

SERIAL_FILE = os.path.join(Config.DATA_PATH, 'serial.json')

def init_serial():
    if not os.path.exists(SERIAL_FILE):
        with open(SERIAL_FILE, 'w') as f:
            json.dump({'next': 2}, f)

def get_next_serial():
    init_serial()
    with open(SERIAL_FILE, 'r+') as f:
        data = json.load(f)
        s = data['next']
        data['next'] += 1
        f.seek(0); f.truncate(); json.dump(data, f)
    return s

def generate_root():
    os.makedirs(Config.DATA_PATH, exist_ok=True)
    init_serial()
    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    subj = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Root CA')])
    cert = x509.CertificateBuilder() \
        .subject_name(subj).issuer_name(issuer) \
        .public_key(key.public_key()) \
        .serial_number(1) \
        .not_valid_before(datetime.utcnow()) \
        .not_valid_after(datetime.utcnow() + timedelta(days=Config.CA_LIFETIME_DAYS)) \
        .add_extension(x509.BasicConstraints(ca=True,path_length=None), critical=True)\
        .sign(key, hashes.SHA256())
    with open(os.path.join(Config.DATA_PATH,'root_key.pem'),'wb') as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()))
    with open(os.path.join(Config.DATA_PATH,'root_cert.pem'),'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    build_crl([])
    return cert, key

def load_root_key():
    with open(os.path.join(Config.DATA_PATH,'root_key.pem'),'rb') as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_root_cert():
    with open(os.path.join(Config.DATA_PATH,'root_cert.pem'),'rb') as f:
        return x509.load_pem_x509_certificate(f.read())

def sign_csr(csr_pem, requester):
    csr = x509.load_pem_x509_csr(csr_pem)
    if not csr.is_signature_valid:
        raise ValueError("CSR signature invalid")
    serial = get_next_serial()
    cert = x509.CertificateBuilder() \
        .subject_name(csr.subject) \
        .issuer_name(load_root_cert().subject) \
        .public_key(csr.public_key()) \
        .serial_number(serial) \
        .not_valid_before(datetime.utcnow()) \
        .not_valid_after(datetime.utcnow() + timedelta(days=Config.CERT_LIFETIME_DAYS)) \
        .add_extension(x509.BasicConstraints(ca=False,path_length=None), critical=True)\
        .sign(load_root_key(), hashes.SHA256())
    issued_dir = os.path.join(Config.DATA_PATH,'issued')
    os.makedirs(issued_dir, exist_ok=True)
    with open(os.path.join(issued_dir,f'{serial}.crt'),'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    meta = {
        'serial': serial,
        'subject': csr.subject.rfc4514_string(),
        'requester': requester,
        'issued_at': datetime.utcnow().isoformat(),
        'revoked': False
    }
    with open(os.path.join(issued_dir,f'{serial}.json'),'w') as f:
        json.dump(meta, f)
    return cert, serial

def load_issued_metadata(data_path):
    issued = []
    d = os.path.join(data_path,'issued')
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.endswith('.json'):
                issued.append(json.load(open(os.path.join(d,fn))))
    return sorted(issued, key=lambda m: m['serial'])

def build_crl(revoked_list):
    builder = x509.CertificateRevocationListBuilder() \
        .issuer_name(load_root_cert().subject) \
        .last_update(datetime.utcnow()) \
        .next_update(datetime.utcnow() + timedelta(days=Config.CERT_LIFETIME_DAYS))
    for m in revoked_list:
        rc = x509.RevokedCertificateBuilder()\
            .serial_number(m['serial'])\
            .revocation_date(datetime.fromisoformat(m['revoked_at']))\
            .build()
        builder = builder.add_revoked_certificate(rc)
    crl = builder.sign(load_root_key(), hashes.SHA256())
    with open(os.path.join(Config.DATA_PATH,'crl.pem'),'wb') as f:
        f.write(crl.public_bytes(serialization.Encoding.PEM))
    return crl

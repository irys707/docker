from flask import session
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

# Simple in-memory user store
_USERS = {}
# initialize default admin
_USERS[Config.ADMIN_USER] = {
    'password_hash': generate_password_hash(Config.ADMIN_PASS),
    'role': 'admin'
}
# optional default requester
_USERS['requester'] = {
    'password_hash': generate_password_hash(Config.ADMIN_PASS),
    'role': 'requester'
}

def authenticate(username, password):
    user = _USERS.get(username)
    if user and check_password_hash(user['password_hash'], password):
        return True
    return False

def login_required(role=None):
    from functools import wraps
    from flask import redirect, url_for, flash
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            user = _USERS.get(session['username'])
            if not user:
                flash('User invalid', 'danger')
                return redirect(url_for('login'))
            if role and user['role'] != role:
                flash('Access denied', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

def add_user(username, password, role='requester'):
    _USERS[username] = {
        'password_hash': generate_password_hash(password),
        'role': role
    }

def get_user_role(username):
    return _USERS.get(username, {}).get('role')

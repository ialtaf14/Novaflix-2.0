import json
import os
import hashlib

USER_DB = 'users.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=4)

def signup(username, name, email, password):
    users = load_users()
    if username in users:
        return False, "Username already exists!"
    
    users[username] = {
        'name': name,
        'email': email,
        'password': hash_password(password),
        'profile': {
            'bio': 'NovaFlix Movie Enthusiast',
            'photo_url': 'https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png'
        },
        'wishlist': [],
        'watched_list': []
    }
    save_users(users)
    return True, "Account created successfully!"

def login(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found!"
    
    if users[username]['password'] == hash_password(password):
        return True, users[username]
    else:
        return False, "Incorrect password!"

def update_password(username, old_password, new_password):
    users = load_users()
    if username not in users:
        return False, "User not found!"
    
    if users[username]['password'] != hash_password(old_password):
        return False, "Incorrect current password!"
    
    users[username]['password'] = hash_password(new_password)
    save_users(users)
    return True, "Password updated successfully!"

def get_user_email(username):
    users = load_users()
    if username in users:
        return users[username].get('email')
    return None

def reset_password(username, new_password):
    users = load_users()
    if username not in users:
        return False, "User not found!"
    
    users[username]['password'] = hash_password(new_password)
    save_users(users)
    return True, "Password reset successfully!"

def is_email_registered(email):
    users = load_users()
    for user_info in users.values():
        if user_info.get('email', '').strip().lower() == email.strip().lower():
            return True
    return False

def validate_username(username):
    import re
    if not username:
        return False, "Username cannot be empty."
    if len(username) > 30:
        return False, "Username must be 30 characters or less."
    if not re.match(r"^[A-Za-z0-9._]+$", username):
        return False, "Allowed characters: letters, numbers, periods (.), and underscores (_)."
    return True, ""

def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isalpha() for c in password):
        return False, "Password must contain at least one letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number."
    return True, ""

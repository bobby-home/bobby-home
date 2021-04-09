import secrets

def generate_key():
    return secrets.token_urlsafe(64)

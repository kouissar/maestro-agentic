import os
import base64
import json
import pickle
from dotenv import load_dotenv

load_dotenv()

def get_secret_file(env_var: str, default_path: str, is_binary: bool = False):
    """
    Retrieves a secret from an environment variable (base64 encoded) 
    or falls back to a local file.
    """
    secret_content = os.getenv(env_var)
    
    if secret_content:
        try:
            # Try to decode base64
            decoded = base64.b64decode(secret_content)
            if is_binary:
                return decoded
            return decoded.decode('utf-8')
        except Exception:
            # If not base64, return as is
            return secret_content
            
    if os.path.exists(default_path):
        mode = 'rb' if is_binary else 'r'
        with open(default_path, mode) as f:
            return f.read()
            
    return None

def get_google_credentials():
    """
    Returns the credentials JSON as a dict.
    """
    content = get_secret_file('GOOGLE_CREDENTIALS_JSON', 'credentials.json')
    if content:
        return json.loads(content)
    return None

def get_gmail_token():
    """
    Returns the tokens as a dict (unpickled).
    """
    content = get_secret_file('GMAIL_TOKEN_PICKLE', 'token.pickle', is_binary=True)
    if content:
        return pickle.loads(content)
    return None

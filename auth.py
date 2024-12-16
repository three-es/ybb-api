from functools import wraps
from flask import request, jsonify
import os
import hmac

# In a production environment, these should be stored securely (e.g., in a database)
API_USERS = {
    "api_user": "your_api_token_here"  # This will be replaced by environment variables
}

def require_api_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        username = request.headers.get('X-API-Username')

        if not auth_header or not username:
            return jsonify({
                'success': False,
                'error': 'Missing authentication credentials'
            }), 401

        # Remove 'Bearer ' prefix if present
        token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else auth_header

        if not is_valid_token(username, token):
            return jsonify({
                'success': False,
                'error': 'Invalid authentication credentials'
            }), 401

        return f(*args, **kwargs)
    return decorated

def is_valid_token(username, token):
    if username not in API_USERS:
        return False
    return hmac.compare_digest(API_USERS[username], token)

# Initialize API credentials from environment variables
def init_api_auth():
    username = os.environ.get('API_USERNAME')
    token = os.environ.get('API_TOKEN')
    if username and token:
        API_USERS[username] = token

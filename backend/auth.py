from functools import wraps
from flask import request, jsonify
import jwt
from datetime import datetime, timedelta
from models import User, UserRole

# JWT Configuration
# Note: In production, use environment variable for secret key
import os
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(days=7)

def generate_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': user.role.value,
        'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user():
    """Get current user from JWT token"""
    token = None
    auth_header = request.headers.get('Authorization')
    
    if auth_header:
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return None
    
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    user = User.query.get(payload['user_id'])
    return user

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is inactive'
            }), 403
        return f(user, *args, **kwargs)
    return decorated_function

def require_role(*allowed_roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(user, *args, **kwargs):
            if user.role.value not in [role.value if isinstance(role, UserRole) else role for role in allowed_roles]:
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions'
                }), 403
            return f(user, *args, **kwargs)
        return decorated_function
    return decorator

def require_student(f):
    """Decorator to require student role"""
    return require_role(UserRole.STUDENT)(f)

def require_mentor(f):
    """Decorator to require mentor role"""
    return require_role(UserRole.MENTOR, UserRole.MANAGER)(f)

def require_manager(f):
    """Decorator to require manager role"""
    return require_role(UserRole.MANAGER)(f)

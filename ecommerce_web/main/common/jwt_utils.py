import jwt
from datetime import datetime, timedelta
from flask import current_app, request


# Generate JWT token (access or refresh)
def generate_token(identity, role, expires_in=3600):
    """Generate a JWT token with identity, role, and expiration time."""
    payload = {
        'identity': identity,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token


# Decode JWT token
def decode_token(token):
    """Decode a JWT token and handle expiration or invalid token errors."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {"code": 401, "message": "Token has expired. Please refresh.", "status": 0}, 401
    except jwt.InvalidTokenError:
        return {"code": 401, "message": "Invalid token provided.", "status": 0}, 401


# JWT required decorator
def jwt_required(f):
    """Decorator to protect routes and ensure a valid JWT token is provided."""
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"code": 401, "message": "Token is missing or invalid", "status": 0}, 401

        token = auth_header.split(" ")[1]
        decoded_token = decode_token(token)
        if isinstance(decoded_token, tuple):  # Handle token errors
            return decoded_token

        request.user = decoded_token
        return f(*args, **kwargs)
    return wrapper


# Role-based access decorator
def role_required(*roles):
    """Decorator to restrict access to certain user roles."""
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_role = request.user.get('role')
            if user_role not in roles:
                return {"code": 403, "message": "Access denied. Insufficient permissions.", "status": 0}, 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Get current user identity
def get_jwt_identity():
    """Retrieve the current user's identity from the token."""
    return request.user.get("identity")


# Get current user role
def get_jwt_role():
    """Retrieve the current user's role from the token."""
    return request.user.get("role")

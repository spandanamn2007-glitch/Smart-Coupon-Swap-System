"""
Authentication & Authorization Decorators
Smart Coupon Swap System
"""

from functools import wraps
from flask import session, jsonify

def login_required(f):
    """Decorator ensuring that the user has an active session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized: Session login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

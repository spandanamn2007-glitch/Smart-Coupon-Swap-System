"""
Authentication Routes
Smart Coupon Swap System

Handles user registration, login, logout, and session state.
Uses Werkzeug password hashing and parameterized SQL queries.
"""

import re
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.db import execute_one, execute_write

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    """User Registration Endpoint."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    city = data.get("city", "").strip() or None
    state = data.get("state", "").strip() or None
    phone = data.get("phone", "").strip() or None
    role_id = data.get("role_id", 2)  # Default to regular User (role_id=2)

    # Validation
    if not name or not email or not password:
        return jsonify({"error": "Missing required fields: name, email, password"}), 400

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Duplicate check
    existing = execute_one("SELECT user_id FROM users WHERE email = %s;", (email,))
    if existing:
        return jsonify({"error": "Email is already registered"}), 400

    # Secure Hash
    hashed_pw = generate_password_hash(password)

    # Insert user
    insert_sql = """
        INSERT INTO users (role_id, name, email, password_hash, phone, city, state)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    try:
        user_id, _ = execute_write(insert_sql, (role_id, name, email, hashed_pw, phone, city, state))

        # Initialize default general preferences
        pref_sql = """
            INSERT INTO user_general_preferences (user_id, min_preferred_discount_pct, max_preferred_expiry_days, preferred_location)
            VALUES (%s, 10.00, 30, %s)
            ON DUPLICATE KEY UPDATE preferred_location = VALUES(preferred_location);
        """
        execute_write(pref_sql, (user_id, city))
    except Exception as e:
        return jsonify({"error": f"Database insertion failed: {str(e)}"}), 500

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role_id": role_id
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """User Login Endpoint."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = execute_one("SELECT user_id, role_id, name, email, password_hash, status FROM users WHERE email = %s;", (email,))
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    if user["status"] != "ACTIVE":
        return jsonify({"error": f"Account status is {user['status']}. Access denied."}), 403

    # Establish session
    session.clear()
    session["user_id"] = user["user_id"]
    session["user_email"] = user["email"]
    session["role_id"] = user["role_id"]

    return jsonify({
        "message": "Login successful",
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "role_id": user["role_id"]
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """User Logout Endpoint."""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    """Returns basic information for the current session."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthenticated"}), 401
    return jsonify({
        "user_id": user_id,
        "email": session.get("user_email"),
        "role_id": session.get("role_id")
    }), 200

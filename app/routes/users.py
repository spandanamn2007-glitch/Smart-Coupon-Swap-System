"""
User Profile & Preference Routes
Smart Coupon Swap System

Provides profile viewing, profile update, and preference endpoints.
Enforces session login and strict authorization boundaries.
"""

from flask import Blueprint, request, jsonify, session
from app.utils.auth_decorator import login_required
from app.services.db import execute_one, execute_write

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """Fetches profile of the currently authenticated user."""
    user_id = session.get("user_id")
    query = """
        SELECT u.user_id, u.role_id, r.role_name, u.name, u.email, u.phone,
               u.city, u.state, u.country, u.status, u.reputation_score, u.created_at
        FROM users u
        JOIN roles r ON u.role_id = r.role_id
        WHERE u.user_id = %s;
    """
    user = execute_one(query, (user_id,))
    if not user:
        return jsonify({"error": "User profile not found"}), 404

    # Convert timestamps/decimals for clean JSON
    user["reputation_score"] = float(user["reputation_score"])
    user["created_at"] = str(user["created_at"])
    return jsonify({"user": user}), 200


@users_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """Updates profile details for the authenticated user."""
    user_id = session.get("user_id")
    data = request.get_json() or {}

    # Authorization Boundary Check: prevent modifying another user's profile
    target_user_id = data.get("user_id")
    if target_user_id and int(target_user_id) != int(user_id):
        return jsonify({"error": "Forbidden: Cannot modify another user's profile"}), 403

    name = data.get("name")
    phone = data.get("phone")
    city = data.get("city")
    state = data.get("state")

    # Build dynamic update
    fields = []
    params = []
    if name is not None:
        fields.append("name = %s")
        params.append(name.strip())
    if phone is not None:
        fields.append("phone = %s")
        params.append(phone.strip() if phone else None)
    if city is not None:
        fields.append("city = %s")
        params.append(city.strip() if city else None)
    if state is not None:
        fields.append("state = %s")
        params.append(state.strip() if state else None)

    if not fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    params.append(user_id)
    update_sql = f"UPDATE users SET {', '.join(fields)} WHERE user_id = %s;"
    execute_write(update_sql, tuple(params))

    # Fetch updated profile
    updated_user = execute_one(
        "SELECT user_id, role_id, name, email, phone, city, state, country, reputation_score FROM users WHERE user_id = %s;",
        (user_id,)
    )
    if updated_user:
        updated_user["reputation_score"] = float(updated_user["reputation_score"])

    return jsonify({
        "message": "Profile updated successfully",
        "user": updated_user
    }), 200


@users_bp.route("/preferences", methods=["GET"])
@login_required
def get_preferences():
    """Fetches preferences for the authenticated user."""
    user_id = session.get("user_id")
    query = """
        SELECT user_id, min_preferred_discount_pct, max_preferred_expiry_days, preferred_location, updated_at
        FROM user_general_preferences
        WHERE user_id = %s;
    """
    prefs = execute_one(query, (user_id,))
    if not prefs:
        # Create default entry if absent
        execute_write(
            "INSERT INTO user_general_preferences (user_id, min_preferred_discount_pct, max_preferred_expiry_days) VALUES (%s, 10.00, 30);",
            (user_id,)
        )
        prefs = execute_one(query, (user_id,))

    if prefs:
        prefs["min_preferred_discount_pct"] = float(prefs["min_preferred_discount_pct"])
        prefs["updated_at"] = str(prefs["updated_at"])

    return jsonify({"preferences": prefs}), 200


@users_bp.route("/preferences", methods=["PUT"])
@login_required
def update_preferences():
    """Updates general preferences for the authenticated user."""
    user_id = session.get("user_id")
    data = request.get_json() or {}

    min_discount = data.get("min_preferred_discount_pct")
    max_expiry = data.get("max_preferred_expiry_days")
    location = data.get("preferred_location")

    fields = []
    params = []
    if min_discount is not None:
        fields.append("min_preferred_discount_pct = %s")
        params.append(float(min_discount))
    if max_expiry is not None:
        fields.append("max_preferred_expiry_days = %s")
        params.append(int(max_expiry))
    if location is not None:
        fields.append("preferred_location = %s")
        params.append(location.strip() if location else None)

    if not fields:
        return jsonify({"error": "No valid preference fields provided"}), 400

    params.append(user_id)
    update_sql = f"UPDATE user_general_preferences SET {', '.join(fields)} WHERE user_id = %s;"
    _, affected = execute_write(update_sql, tuple(params))

    if affected == 0:
        # Insert if row didn't exist
        execute_write(
            "INSERT INTO user_general_preferences (user_id, min_preferred_discount_pct, max_preferred_expiry_days, preferred_location) VALUES (%s, %s, %s, %s);",
            (user_id, float(min_discount or 10.0), int(max_expiry or 30), location)
        )

    updated_prefs = execute_one(
        "SELECT user_id, min_preferred_discount_pct, max_preferred_expiry_days, preferred_location FROM user_general_preferences WHERE user_id = %s;",
        (user_id,)
    )
    if updated_prefs:
        updated_prefs["min_preferred_discount_pct"] = float(updated_prefs["min_preferred_discount_pct"])

    return jsonify({
        "message": "Preferences updated successfully",
        "preferences": updated_prefs
    }), 200

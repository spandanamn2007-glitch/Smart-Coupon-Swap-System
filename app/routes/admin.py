"""
Admin Dashboard API Routes
Smart Coupon Swap System

Provides system-level aggregated statistics for admin users (role_id=1).
"""

from flask import Blueprint, jsonify, session
from app.services.db import execute_one

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _require_admin():
    """Returns user_id if admin, else None."""
    if not session.get("user_id"):
        return None, (jsonify({"error": "Unauthenticated"}), 401)
    if session.get("role_id") != 1:
        return None, (jsonify({"error": "Forbidden: Admin access required"}), 403)
    return session["user_id"], None


@admin_bp.route("/stats", methods=["GET"])
def get_admin_stats():
    """Returns aggregated system statistics for admin dashboard."""
    _, err = _require_admin()
    if err:
        return err

    stats = {}

    row = execute_one("SELECT COUNT(*) AS cnt FROM users;")
    stats["total_users"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM coupons;")
    stats["total_coupons"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM coupons WHERE status = 'ACTIVE' AND expiry_date >= CURRENT_DATE();")
    stats["active_coupons"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM coupon_requests;")
    stats["total_requests"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM swaps;")
    stats["total_swaps"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM swaps WHERE status = 'COMPLETED';")
    stats["completed_swaps"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM reports WHERE status = 'OPEN';")
    stats["open_reports"] = row["cnt"] if row else 0

    row = execute_one("SELECT COUNT(*) AS cnt FROM users WHERE status = 'ACTIVE';")
    stats["active_users"] = row["cnt"] if row else 0

    return jsonify({"stats": stats}), 200

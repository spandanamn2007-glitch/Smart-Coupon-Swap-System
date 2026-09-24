"""
Health Check Route
Smart Coupon Swap System
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Simple status check endpoint returning HTTP 200."""
    return jsonify({
        "status": "ok",
        "service": "Smart Coupon Swap System API",
        "phase": "Phase 6 (Feature Engineering & Backend Foundation)"
    }), 200

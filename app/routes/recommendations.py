"""
Recommendation Routes
Smart Coupon Swap System

Provides explainable recommendation API for authenticated users.
"""

from flask import Blueprint, jsonify, session, request
from app.utils.auth_decorator import login_required
from app.services.recommendation_service import get_recommendations_for_user

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendations_bp.route("", methods=["GET"])
@login_required
def get_user_recommendations():
    """Returns explainable recommendations for the authenticated user."""
    user_id = session.get("user_id")
    limit = int(request.args.get("limit", 10))

    recs = get_recommendations_for_user(user_id, limit=limit)
    
    # Format floating numbers for clean JSON
    for item in recs:
        c = item["coupon"]
        c["coupon_value"] = float(c["coupon_value"])
        c["discount_value"] = float(c["discount_value"])
        c["minimum_purchase"] = float(c["minimum_purchase"])
        c["issue_date"] = str(c["issue_date"])
        c["expiry_date"] = str(c["expiry_date"])

    return jsonify({
        "user_id": user_id,
        "count": len(recs),
        "recommendations": recs
    }), 200

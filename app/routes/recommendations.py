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
        val = float(c.get("discount_value") or c.get("coupon_value") or 0.0)
        min_p = float(c.get("min_purchase_amount") or c.get("minimum_purchase") or 0.0)
        c["discount_value"] = val
        c["coupon_value"] = val
        c["min_purchase_amount"] = min_p
        c["minimum_purchase"] = min_p
        if c.get("issue_date"):
            c["issue_date"] = str(c["issue_date"])
        if c.get("expiry_date"):
            c["expiry_date"] = str(c["expiry_date"])

    return jsonify({
        "user_id": user_id,
        "count": len(recs),
        "recommendations": recs
    }), 200

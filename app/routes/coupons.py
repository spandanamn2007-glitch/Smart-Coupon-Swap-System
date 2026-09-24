"""
Coupon Marketplace & Search Routes
Smart Coupon Swap System

Provides CRUD operations, search, and filtering endpoints for coupon listings.
"""

from flask import Blueprint, request, jsonify, session
from app.utils.auth_decorator import login_required
from app.services.coupon_service import (
    create_coupon, get_coupon_by_id, update_coupon, delete_coupon, search_coupons
)

coupons_bp = Blueprint("coupons", __name__, url_prefix="/api/coupons")


@coupons_bp.route("", methods=["GET"])
def list_coupons():
    """Browse, search, and filter coupons."""
    params = request.args.to_dict()
    results = search_coupons(params)
    for r in results:
        r["discount_value"] = float(r["discount_value"]) if r.get("discount_value") is not None else 0.0
        r["min_purchase_amount"] = float(r["min_purchase_amount"]) if r.get("min_purchase_amount") is not None else 0.0
        r["issue_date"] = str(r["issue_date"]) if r.get("issue_date") else ""
        r["expiry_date"] = str(r["expiry_date"]) if r.get("expiry_date") else ""
    return jsonify({"count": len(results), "coupons": results}), 200


@coupons_bp.route("/<int:coupon_id>", methods=["GET"])
def view_coupon(coupon_id):
    """View details of a single coupon."""
    coupon = get_coupon_by_id(coupon_id)
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404

    coupon["discount_value"] = float(coupon["discount_value"]) if coupon.get("discount_value") is not None else 0.0
    coupon["min_purchase_amount"] = float(coupon["min_purchase_amount"]) if coupon.get("min_purchase_amount") is not None else 0.0
    coupon["issue_date"] = str(coupon["issue_date"]) if coupon.get("issue_date") else ""
    coupon["expiry_date"] = str(coupon["expiry_date"]) if coupon.get("expiry_date") else ""
    return jsonify({"coupon": coupon}), 200


@coupons_bp.route("", methods=["POST"])
@login_required
def add_coupon():
    """Create a new coupon listing for the authenticated user."""
    owner_id = session.get("user_id")
    data = request.get_json() or {}

    try:
        new_coupon = create_coupon(owner_id, data)
        new_coupon["discount_value"] = float(new_coupon["discount_value"]) if new_coupon.get("discount_value") is not None else 0.0
        new_coupon["min_purchase_amount"] = float(new_coupon["min_purchase_amount"]) if new_coupon.get("min_purchase_amount") is not None else 0.0
        new_coupon["issue_date"] = str(new_coupon["issue_date"]) if new_coupon.get("issue_date") else ""
        new_coupon["expiry_date"] = str(new_coupon["expiry_date"]) if new_coupon.get("expiry_date") else ""
        return jsonify({"message": "Coupon created successfully", "coupon": new_coupon}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create coupon: {str(e)}"}), 500


@coupons_bp.route("/<int:coupon_id>", methods=["PUT"])
@login_required
def edit_coupon(coupon_id):
    """Update details of an existing coupon owned by authenticated user."""
    owner_id = session.get("user_id")
    data = request.get_json() or {}

    updated, err = update_coupon(coupon_id, owner_id, data)
    if err:
        status_code = 403 if "Forbidden" in err else (404 if "not found" in err else 400)
        return jsonify({"error": err}), status_code

    if updated:
        updated["discount_value"] = float(updated["discount_value"]) if updated.get("discount_value") is not None else 0.0
        updated["min_purchase_amount"] = float(updated["min_purchase_amount"]) if updated.get("min_purchase_amount") is not None else 0.0
        updated["issue_date"] = str(updated["issue_date"]) if updated.get("issue_date") else ""
        updated["expiry_date"] = str(updated["expiry_date"]) if updated.get("expiry_date") else ""

    return jsonify({"message": "Coupon updated successfully", "coupon": updated}), 200


@coupons_bp.route("/<int:coupon_id>", methods=["DELETE"])
@login_required
def remove_coupon(coupon_id):
    """Deactivates a coupon owned by the authenticated user."""
    owner_id = session.get("user_id")
    success, err = delete_coupon(coupon_id, owner_id)
    if err:
        status_code = 403 if "Forbidden" in err else 404
        return jsonify({"error": err}), status_code

    return jsonify({"message": "Coupon removed successfully"}), 200

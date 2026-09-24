"""
Swap Engine Routes
Smart Coupon Swap System

Provides bilateral 2-way swap compatibility scoring and 3-way circular cycle detection APIs.
"""

from flask import Blueprint, request, jsonify
from app.services.swap_service import calculate_swap_compatibility
from app.services.graph_service import detect_swap_cycles

swaps_bp = Blueprint("swaps", __name__, url_prefix="/api/swaps")


@swaps_bp.route("/compatibility", methods=["POST"])
def evaluate_compatibility():
    """Evaluates bilateral 2-way swap compatibility score between two coupons."""
    data = request.get_json() or {}
    offered_id = data.get("offered_coupon_id")
    requested_id = data.get("requested_coupon_id")

    if not offered_id or not requested_id:
        return jsonify({"error": "Missing required fields: offered_coupon_id, requested_coupon_id"}), 400

    result, err = calculate_swap_compatibility(offered_id, requested_id)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200


@swaps_bp.route("/cycles", methods=["GET"])
def get_swap_cycles():
    """Detects 3-way and multi-user circular swap opportunities using graph traversal."""
    max_len = int(request.args.get("max_length", 3))
    cycles = detect_swap_cycles(max_cycle_length=max_len)
    return jsonify({
        "count": len(cycles),
        "cycles": cycles
    }), 200

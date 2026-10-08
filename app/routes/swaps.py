"""
Swap Engine Routes
Smart Coupon Swap System

Provides bilateral 2-way swap compatibility scoring, 3-way circular cycle
detection, and exchange request management (create, list, accept, reject).
"""

from flask import Blueprint, request, jsonify, session
from app.services.swap_service import calculate_swap_compatibility
from app.services.graph_service import detect_swap_cycles
from app.services.exchange_service import (
    create_exchange_request,
    get_incoming_requests,
    get_outgoing_requests,
    accept_exchange,
    reject_exchange,
)
from app.utils.auth_decorator import login_required

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


@swaps_bp.route("/requests", methods=["GET"])
@login_required
def list_swap_requests():
    """Retrieves exchange requests for the logged-in user."""
    user_id = session.get("user_id")
    incoming = get_incoming_requests(user_id)
    outgoing = get_outgoing_requests(user_id)
    return jsonify({
        "count": len(incoming),
        "requests": incoming,
        "incoming": incoming,
        "outgoing": outgoing
    }), 200


@swaps_bp.route("/requests", methods=["POST"])
@swaps_bp.route("/request", methods=["POST"])
@login_required
def create_swap_request():
    """Creates a new exchange/swap proposal."""
    initiator_id = session.get("user_id")
    data = request.get_json() or {}
    offered_id = data.get("offered_coupon_id")
    requested_id = data.get("requested_coupon_id")

    if not offered_id or not requested_id:
        return jsonify({"error": "Missing required fields: offered_coupon_id, requested_coupon_id"}), 400

    try:
        offered_id = int(offered_id)
        requested_id = int(requested_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coupon IDs provided"}), 400

    swap_id, err = create_exchange_request(initiator_id, offered_id, requested_id)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({
        "message": "Exchange request created successfully",
        "swap_id": swap_id
    }), 201


@swaps_bp.route("/requests/<int:swap_id>/accept", methods=["POST"])
@login_required
def accept_swap_request(swap_id):
    """Accepts a pending exchange request."""
    user_id = session.get("user_id")
    swap, err = accept_exchange(swap_id, user_id)
    if err:
        status_code = 403 if "Forbidden" in err else (404 if "not found" in err else 400)
        return jsonify({"error": err}), status_code

    return jsonify({
        "message": "Exchange accepted and completed successfully",
        "swap": swap
    }), 200


@swaps_bp.route("/requests/<int:swap_id>/reject", methods=["POST"])
@login_required
def reject_swap_request(swap_id):
    """Rejects a pending exchange request."""
    user_id = session.get("user_id")
    res, err = reject_exchange(swap_id, user_id)
    if err:
        status_code = 403 if "Forbidden" in err else (404 if "not found" in err else 400)
        return jsonify({"error": err}), status_code

    return jsonify({
        "message": "Exchange request rejected successfully",
        "swap_id": res
    }), 200


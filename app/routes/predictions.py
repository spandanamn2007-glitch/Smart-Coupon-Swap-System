"""
Machine Learning & Analytics Routes
Smart Coupon Swap System

Exposes acceptance prediction, anomaly detection, and demand forecasting endpoints.
"""

from flask import Blueprint, request, jsonify
from app.services.prediction_service import (
    predict_acceptance, detect_user_anomalies, forecast_demand
)

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")


@predictions_bp.route("/acceptance", methods=["POST"])
def predict_swap_acceptance():
    """Predicts likelihood of swap proposal acceptance."""
    data = request.get_json() or {}
    offered_val = data.get("offered_value")
    req_val = data.get("requested_value")
    cat_match = data.get("category_match", 0)
    brand_match = data.get("brand_match", 0)
    p_rating = data.get("proposer_rating", 3.0)
    r_rating = data.get("receiver_rating", 3.0)

    if offered_val is None or req_val is None:
        return jsonify({"error": "Missing required fields: offered_value, requested_value"}), 400

    result, err = predict_acceptance(float(offered_val), float(req_val), cat_match, brand_match, p_rating, r_rating)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200


@predictions_bp.route("/anomalies", methods=["GET"])
def get_user_anomalies():
    """Detects potential user behavioral anomalies using IsolationForest."""
    limit = int(request.args.get("limit", 20))
    result, err = detect_user_anomalies(limit=limit)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200


@predictions_bp.route("/demand", methods=["POST"])
def predict_category_demand():
    """Forecasts expected category demand for next month."""
    data = request.get_json() or {}
    prev_reqs = data.get("prev_month_requests")

    if prev_reqs is None:
        return jsonify({"error": "Missing required field: prev_month_requests"}), 400

    result, err = forecast_demand(float(prev_reqs))
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200

"""
Machine Learning Prediction & Anomaly Service
Smart Coupon Swap System

Loads model artifacts from models/ and executes:
1. Swap Acceptance Probability Prediction
2. User Anomaly Flagging
3. Category Demand Forecasting
"""

import os
import joblib
import pandas as pd
import numpy as np
from app.services.db import execute_all

# Resolve paths relative to this file's location so they work
# both locally and in Vercel's serverless environment.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# services/ -> app/ -> project_root/
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
FEATURES_DIR = os.path.join(PROJECT_ROOT, "data", "features")

# Fallback: if the above doesn't exist (e.g. symlinked deploy),
# try resolving from the current working directory as well.
if not os.path.isdir(MODELS_DIR):
    MODELS_DIR = os.path.join(os.getcwd(), "models")
if not os.path.isdir(FEATURES_DIR):
    FEATURES_DIR = os.path.join(os.getcwd(), "data", "features")



def predict_acceptance(offered_value, requested_value, cat_match, brand_match, proposer_rating=3.0, receiver_rating=3.0):
    """Predicts the probability of a swap proposal being accepted."""
    model_path = os.path.join(MODELS_DIR, "acceptance_model.joblib")
    if not os.path.isfile(model_path):
        return None, "Acceptance model artifact not found"

    artifact = joblib.load(model_path)
    model = artifact["model"]

    v_diff = abs(offered_value - requested_value)
    v_ratio = round(offered_value / (requested_value + 1e-5), 4)

    input_data = pd.DataFrame([{
        "value_difference": v_diff,
        "value_ratio": v_ratio,
        "category_match": int(cat_match),
        "brand_match": int(brand_match),
        "proposer_avg_rating": float(proposer_rating),
        "receiver_avg_rating": float(receiver_rating)
    }])

    prob = float(model.predict_proba(input_data)[0, 1])
    is_likely = prob >= 0.50

    return {
        "acceptance_probability": round(prob, 4),
        "acceptance_percentage": round(prob * 100, 2),
        "is_likely_accepted": is_likely,
        "features_input": {
            "value_difference": v_diff,
            "value_ratio": v_ratio,
            "category_match": cat_match,
            "brand_match": brand_match,
            "proposer_rating": proposer_rating,
            "receiver_rating": receiver_rating
        }
    }, None


def detect_user_anomalies(limit=20):
    """Flags potential user behavioral anomalies using IsolationForest."""
    model_path = os.path.join(MODELS_DIR, "anomaly_model.joblib")
    uf_path = os.path.join(FEATURES_DIR, "user_features.csv")

    if not os.path.isfile(model_path) or not os.path.isfile(uf_path):
        return None, "Anomaly model or user feature file not found"

    artifact = joblib.load(model_path)
    model = artifact["model"]
    feature_cols = artifact["features"]

    uf = pd.read_csv(uf_path)
    X = uf[feature_cols].fillna(0)

    preds = model.predict(X)
    scores = model.decision_function(X)

    uf["anomaly_flag"] = np.where(preds == -1, "potential_anomaly", "normal")
    uf["anomaly_score"] = scores.round(4)

    anomalies = uf[uf["anomaly_flag"] == "potential_anomaly"].sort_values("anomaly_score")

    results = []
    for _, row in anomalies.head(limit).iterrows():
        results.append({
            "user_id": row["user_id"],
            "age": int(row["age"]),
            "activity_level": row["activity_level"],
            "total_views": int(row["total_views_count"]),
            "total_requests": int(row["total_requests_count"]),
            "swaps_proposed": int(row["swaps_proposed_count"]),
            "anomaly_score": float(row["anomaly_score"]),
            "status_label": "potential_anomaly"
        })

    return {
        "total_users_scanned": len(uf),
        "total_anomalies_detected": len(anomalies),
        "anomalous_users": results
    }, None


def forecast_demand(prev_month_requests):
    """Forecasts expected category requests for next month based on lag demand."""
    model_path = os.path.join(MODELS_DIR, "demand_model.joblib")
    if not os.path.isfile(model_path):
        return None, "Demand model artifact not found"

    artifact = joblib.load(model_path)
    model = artifact["model"]

    input_df = pd.DataFrame([{"prev_month_requests": float(prev_month_requests)}])
    pred = float(model.predict(input_df)[0])

    return {
        "previous_month_requests": prev_month_requests,
        "forecasted_next_month_requests": round(pred, 2),
        "growth_estimate_pct": round(((pred - prev_month_requests) / (prev_month_requests + 1e-5)) * 100, 2)
    }, None

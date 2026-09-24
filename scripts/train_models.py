"""
Phase 7 Machine Learning Training Pipeline
Smart Coupon Swap System

Trains and exports ML models:
1. Acceptance Prediction Model (RandomForestClassifier -> models/acceptance_model.joblib)
2. User Anomaly Detection Model (IsolationForest -> models/anomaly_model.joblib)
3. Category Demand Forecast Model (RandomForestRegressor -> models/demand_model.joblib)

Outputs model metrics summary to outputs/model_metrics.json.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, mean_absolute_error, root_mean_squared_error, r2_score

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
FEATURES_DIR = os.path.join(PROJECT_ROOT, "data", "features")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def train_acceptance_model():
    print("Training Acceptance Prediction Model...")
    spf = pd.read_csv(os.path.join(FEATURES_DIR, "swap_pair_features.csv"))
    
    # Filter for resolved swaps (accepted/completed = 1 vs rejected/cancelled = 0)
    resolved = spf[spf["swap_status"].isin(["accepted", "completed", "rejected", "cancelled"])].copy()
    resolved["target"] = np.where(resolved["swap_status"].isin(["accepted", "completed"]), 1, 0)
    
    feature_cols = ["value_difference", "value_ratio", "category_match", "brand_match", "proposer_avg_rating", "receiver_avg_rating"]
    X = resolved[feature_cols]
    y = resolved["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    
    metrics = {
        "model_type": "RandomForestClassifier",
        "sample_size": len(resolved),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "features_used": feature_cols
    }
    
    model_path = os.path.join(MODELS_DIR, "acceptance_model.joblib")
    joblib.dump({"model": clf, "features": feature_cols}, model_path)
    print(f"  [OK] Saved acceptance model to {model_path}")
    print(f"       Accuracy: {metrics['accuracy']}, F1: {metrics['f1_score']}, ROC-AUC: {metrics['roc_auc']}")
    return metrics


def train_anomaly_model():
    print("Training User Anomaly Detection Model...")
    uf = pd.read_csv(os.path.join(FEATURES_DIR, "user_features.csv"))
    
    feature_cols = [
        "age", "preferred_discount_range", "total_views_count", "avg_view_duration",
        "total_requests_count", "accepted_requests_count", "total_usage_count",
        "swaps_proposed_count", "swaps_received_count", "avg_rating_received"
    ]
    X = uf[feature_cols].fillna(0)
    
    iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    iso.fit(X)
    
    predictions = iso.predict(X)
    anomaly_count = int((predictions == -1).sum())
    
    metrics = {
        "model_type": "IsolationForest",
        "sample_size": len(uf),
        "features_used": feature_cols,
        "contamination": 0.05,
        "anomalies_detected": anomaly_count,
        "anomaly_percentage": round((anomaly_count / len(uf)) * 100, 2)
    }
    
    model_path = os.path.join(MODELS_DIR, "anomaly_model.joblib")
    joblib.dump({"model": iso, "features": feature_cols}, model_path)
    print(f"  [OK] Saved anomaly model to {model_path}")
    print(f"       Detected {anomaly_count} potential anomalies ({metrics['anomaly_percentage']}%)")
    return metrics


def train_demand_model():
    print("Training Category Demand Forecast Model...")
    requests = pd.read_csv(os.path.join(PROCESSED_DIR, "coupon_requests_clean.csv"))
    coupons = pd.read_csv(os.path.join(PROCESSED_DIR, "coupons_clean.csv"))
    
    # Merge requests with coupons to get category_id and month
    req_c = requests.merge(coupons[["coupon_id", "category_id"]], on="coupon_id")
    req_c["year_month"] = pd.to_datetime(req_c["requested_at"]).dt.to_period("M").astype(str)
    
    # Aggregate demand per category per month
    demand_df = req_c.groupby(["category_id", "year_month"]).size().reset_index(name="monthly_requests")
    
    # Sort and create lag feature
    demand_df = demand_df.sort_values(["category_id", "year_month"])
    demand_df["prev_month_requests"] = demand_df.groupby("category_id")["monthly_requests"].shift(1)
    demand_df = demand_df.dropna()
    
    if len(demand_df) < 10:
        print("  Notice: Limited temporal depth for complex forecasting. Fitting baseline regressor.")
    
    X = demand_df[["prev_month_requests"]]
    y = demand_df["monthly_requests"]
    
    reg = RandomForestRegressor(n_estimators=50, random_state=42)
    reg.fit(X, y)
    
    y_pred = reg.predict(X)
    mae = mean_absolute_error(y, y_pred)
    rmse = root_mean_squared_error(y, y_pred)
    r2 = r2_score(y, y_pred)
    
    metrics = {
        "model_type": "RandomForestRegressor",
        "sample_size": len(demand_df),
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "r2_score": round(float(r2), 4)
    }
    
    model_path = os.path.join(MODELS_DIR, "demand_model.joblib")
    joblib.dump({"model": reg, "features": ["prev_month_requests"]}, model_path)
    print(f"  [OK] Saved demand model to {model_path}")
    print(f"       MAE: {metrics['mae']}, RMSE: {metrics['rmse']}, R2: {metrics['r2_score']}")
    return metrics


def main():
    print("=" * 65)
    print("PHASE 7 - MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 65)
    
    acc_m = train_acceptance_model()
    anom_m = train_anomaly_model()
    dem_m = train_demand_model()
    
    all_metrics = {
        "acceptance_prediction": acc_m,
        "anomaly_detection": anom_m,
        "demand_forecasting": dem_m
    }
    
    out_path = os.path.join(OUTPUTS_DIR, "model_metrics.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nModel metrics saved to {out_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()

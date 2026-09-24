"""
Phase 6 — Feature Engineering Pipeline
Smart Coupon Swap System

Reads cleaned datasets from data/processed/*.csv and generates feature datasets in data/features/*.csv.
Leakage Prevention: All feature aggregations are strictly descriptive or historical.
Outputs:
  - data/features/user_features.csv
  - data/features/coupon_features.csv
  - data/features/interaction_features.csv
  - data/features/swap_pair_features.csv
"""

import os
import sys
import pandas as pd
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
FEATURES_DIR = os.path.join(PROJECT_ROOT, "data", "features")

os.makedirs(FEATURES_DIR, exist_ok=True)


def load_processed_data():
    files = {
        "categories": "categories_clean.csv",
        "brands": "brands_clean.csv",
        "users": "users_clean.csv",
        "coupons": "coupons_clean.csv",
        "user_preferences": "user_preferences_clean.csv",
        "coupon_views": "coupon_views_clean.csv",
        "coupon_requests": "coupon_requests_clean.csv",
        "coupon_usage": "coupon_usage_clean.csv",
        "swaps": "swaps_clean.csv",
        "ratings": "ratings_clean.csv",
    }
    dfs = {}
    for k, v in files.items():
        dfs[k] = pd.read_csv(os.path.join(PROCESSED_DIR, v))
    return dfs


def build_user_features(dfs):
    print("Building user features...")
    users = dfs["users"].copy()
    views = dfs["coupon_views"]
    requests = dfs["coupon_requests"]
    usage = dfs["coupon_usage"]
    swaps = dfs["swaps"]
    ratings = dfs["ratings"]
    prefs = dfs["user_preferences"]

    # Demographic & preference range features
    users["preferred_discount_range"] = users["preferred_discount_max"] - users["preferred_discount_min"]

    # View telemetry aggregations
    v_agg = views.groupby("user_id").agg(
        total_views_count=("view_id", "count"),
        avg_view_duration=("view_duration_seconds", "mean")
    ).reset_index()

    # Request aggregations
    r_agg = requests.groupby("user_id").agg(
        total_requests_count=("request_id", "count"),
        accepted_requests_count=("request_status", lambda x: (x == "accepted").sum())
    ).reset_index()

    # Usage aggregations
    u_agg = usage.groupby("user_id").agg(
        total_usage_count=("usage_id", "count")
    ).reset_index()

    # Swap participation
    s_prop = swaps.groupby("proposer_id").agg(swaps_proposed_count=("swap_id", "count")).reset_index().rename(columns={"proposer_id": "user_id"})
    s_recv = swaps.groupby("receiver_id").agg(swaps_received_count=("swap_id", "count")).reset_index().rename(columns={"receiver_id": "user_id"})

    # Swaps completed involving user
    comp_swaps = swaps[swaps["swap_status"].isin(["completed", "accepted"])]
    s_comp_p = comp_swaps.groupby("proposer_id").agg(comp_p=("swap_id", "count")).reset_index().rename(columns={"proposer_id": "user_id"})
    s_comp_r = comp_swaps.groupby("receiver_id").agg(comp_r=("swap_id", "count")).reset_index().rename(columns={"receiver_id": "user_id"})

    # Rating reputation received
    rat_agg = ratings.groupby("rated_user_id").agg(
        avg_rating_received=("rating", "mean"),
        ratings_count=("rating", "count")
    ).reset_index().rename(columns={"rated_user_id": "user_id"})

    # Preference count
    pref_agg = prefs.groupby("user_id").agg(total_preferences_count=("preference_id", "count")).reset_index()

    # Merge all user feature blocks
    uf = users.merge(v_agg, on="user_id", how="left")
    uf = uf.merge(r_agg, on="user_id", how="left")
    uf = uf.merge(u_agg, on="user_id", how="left")
    uf = uf.merge(s_prop, on="user_id", how="left")
    uf = uf.merge(s_recv, on="user_id", how="left")
    uf = uf.merge(s_comp_p, on="user_id", how="left")
    uf = uf.merge(s_comp_r, on="user_id", how="left")
    uf = uf.merge(rat_agg, on="user_id", how="left")
    uf = uf.merge(pref_agg, on="user_id", how="left")

    uf["comp_p"] = uf["comp_p"].fillna(0)
    uf["comp_r"] = uf["comp_r"].fillna(0)
    uf["swaps_completed_count"] = (uf["comp_p"] + uf["comp_r"]).astype(int)
    uf.drop(columns=["comp_p", "comp_r"], inplace=True)

    # Fill numerical NaNs for zero-activity cases
    count_cols = [
        "total_views_count", "total_requests_count", "accepted_requests_count",
        "total_usage_count", "swaps_proposed_count", "swaps_received_count",
        "ratings_count", "total_preferences_count"
    ]
    uf[count_cols] = uf[count_cols].fillna(0).astype(int)
    uf["avg_view_duration"] = uf["avg_view_duration"].fillna(0.0).round(2)
    uf["avg_rating_received"] = uf["avg_rating_received"].fillna(0.0).round(2)

    return uf


def build_coupon_features(dfs):
    print("Building coupon features...")
    coupons = dfs["coupons"].copy()
    views = dfs["coupon_views"]
    requests = dfs["coupon_requests"]
    usage = dfs["coupon_usage"]
    swaps = dfs["swaps"]

    # Validity duration in days
    coupons["validity_duration_days"] = (pd.to_datetime(coupons["expiry_date"]) - pd.to_datetime(coupons["issue_date"])).dt.days

    # Effective discount percentage calculation
    coupons["effective_discount_pct"] = np.where(
        coupons["discount_type"] == "percentage",
        coupons["discount_value"],
        (coupons["discount_value"] / (coupons["coupon_value"] + 1e-5)) * 100.0
    ).round(2)

    # View telemetry per coupon
    v_agg = views.groupby("coupon_id").agg(
        total_views_count=("view_id", "count"),
        avg_view_duration=("view_duration_seconds", "mean")
    ).reset_index()

    # Request telemetry per coupon
    r_agg = requests.groupby("coupon_id").agg(
        total_requests_count=("request_id", "count")
    ).reset_index()

    # Usage telemetry per coupon
    u_agg = usage.groupby("coupon_id").agg(
        total_usage_count=("usage_id", "count")
    ).reset_index()

    # Swap appearances
    s_off = swaps.groupby("offered_coupon_id").agg(swap_offered_count=("swap_id", "count")).reset_index().rename(columns={"offered_coupon_id": "coupon_id"})
    s_req = swaps.groupby("requested_coupon_id").agg(swap_requested_count=("swap_id", "count")).reset_index().rename(columns={"requested_coupon_id": "coupon_id"})

    cf = coupons.merge(v_agg, on="coupon_id", how="left")
    cf = cf.merge(r_agg, on="coupon_id", how="left")
    cf = cf.merge(u_agg, on="coupon_id", how="left")
    cf = cf.merge(s_off, on="coupon_id", how="left")
    cf = cf.merge(s_req, on="coupon_id", how="left")

    count_cols = ["total_views_count", "total_requests_count", "total_usage_count", "swap_offered_count", "swap_requested_count"]
    cf[count_cols] = cf[count_cols].fillna(0).astype(int)
    cf["avg_view_duration"] = cf["avg_view_duration"].fillna(0.0).round(2)

    # Request conversion rate
    cf["request_conversion_rate"] = np.where(
        cf["total_views_count"] > 0,
        (cf["total_requests_count"] / cf["total_views_count"]).round(4),
        0.0
    )

    return cf


def build_interaction_features(dfs):
    print("Building user-coupon interaction features...")
    views = dfs["coupon_views"]
    requests = dfs["coupon_requests"]
    usage = dfs["coupon_usage"]

    v_agg = views.groupby(["user_id", "coupon_id"]).agg(
        view_count=("view_id", "count"),
        total_view_duration=("view_duration_seconds", "sum")
    ).reset_index()

    r_agg = requests.groupby(["user_id", "coupon_id"]).agg(
        request_count=("request_id", "count")
    ).reset_index()

    u_agg = usage.groupby(["user_id", "coupon_id"]).agg(
        usage_count=("usage_id", "count")
    ).reset_index()

    inter = v_agg.merge(r_agg, on=["user_id", "coupon_id"], how="outer")
    inter = inter.merge(u_agg, on=["user_id", "coupon_id"], how="outer")

    inter["view_count"] = inter["view_count"].fillna(0).astype(int)
    inter["total_view_duration"] = inter["total_view_duration"].fillna(0).astype(int)
    inter["request_count"] = inter["request_count"].fillna(0).astype(int)
    inter["usage_count"] = inter["usage_count"].fillna(0).astype(int)

    # Weighted interaction score (Views * 1 + Requests * 3 + Usage * 5)
    inter["interaction_score"] = (
        inter["view_count"] * 1 +
        inter["request_count"] * 3 +
        inter["usage_count"] * 5
    )

    return inter


def build_swap_pair_features(dfs):
    print("Building swap pair features...")
    swaps = dfs["swaps"].copy()
    coupons = dfs["coupons"].set_index("coupon_id")
    ratings = dfs["ratings"]

    proposer_ratings = ratings.groupby("rated_user_id")["rating"].mean().to_dict()

    rows = []
    for _, row in swaps.iterrows():
        sid = row["swap_id"]
        offered_id = row["offered_coupon_id"]
        requested_id = row["requested_coupon_id"]

        offered_c = coupons.loc[offered_id] if offered_id in coupons.index else None
        requested_c = coupons.loc[requested_id] if requested_id in coupons.index else None

        if offered_c is not None and requested_c is not None:
            v_diff = abs(offered_c["coupon_value"] - requested_c["coupon_value"])
            v_ratio = round(offered_c["coupon_value"] / (requested_c["coupon_value"] + 1e-5), 4)
            cat_match = int(offered_c["category_id"] == requested_c["category_id"])
            brand_match = int(offered_c["brand_id"] == requested_c["brand_id"])
        else:
            v_diff = 0.0
            v_ratio = 1.0
            cat_match = 0
            brand_match = 0

        p_rating = proposer_ratings.get(row["proposer_id"], 3.0)
        r_rating = proposer_ratings.get(row["receiver_id"], 3.0)

        turnaround = np.nan
        if pd.notnull(row["completed_at"]) and pd.notnull(row["proposed_at"]):
            t_diff = (pd.to_datetime(row["completed_at"]) - pd.to_datetime(row["proposed_at"])).total_seconds() / 3600.0
            turnaround = round(t_diff, 2)

        rows.append({
            "swap_id": sid,
            "proposer_id": row["proposer_id"],
            "receiver_id": row["receiver_id"],
            "offered_coupon_id": offered_id,
            "requested_coupon_id": requested_id,
            "value_difference": round(v_diff, 2),
            "value_ratio": v_ratio,
            "category_match": cat_match,
            "brand_match": brand_match,
            "proposer_avg_rating": round(p_rating, 2),
            "receiver_avg_rating": round(r_rating, 2),
            "swap_turnaround_hours": turnaround,
            "swap_status": row["swap_status"]
        })

    return pd.DataFrame(rows)


def main():
    print("=" * 65)
    print("PHASE 6 — FEATURE ENGINEERING PIPELINE")
    print("=" * 65)
    dfs = load_processed_data()

    uf = build_user_features(dfs)
    cf = build_coupon_features(dfs)
    inter = build_interaction_features(dfs)
    spf = build_swap_pair_features(dfs)

    out_map = {
        "user_features.csv": uf,
        "coupon_features.csv": cf,
        "interaction_features.csv": inter,
        "swap_pair_features.csv": spf
    }

    print("\nWriting feature datasets to data/features/:")
    for name, df in out_map.items():
        p = os.path.join(FEATURES_DIR, name)
        df.to_csv(p, index=False)
        print(f"  [OK] {name:<26} : {len(df):>6} rows, {len(df.columns):>2} cols")

    print("=" * 65)
    print("Feature Engineering completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()

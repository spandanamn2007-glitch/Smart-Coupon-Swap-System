"""
Phase 3 Dataset Validation Script
Smart Coupon Swap System

Performs read-only validation of generated raw CSV datasets in data/raw/.
Does NOT modify, clean, or transform datasets.
Reports PASS/FAIL for each validation rule.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")

EXPECTED_FILES = [
    "categories.csv",
    "brands.csv",
    "users.csv",
    "coupons.csv",
    "user_preferences.csv",
    "coupon_views.csv",
    "coupon_requests.csv",
    "coupon_usage.csv",
    "swaps.csv",
    "ratings.csv"
]

EXPECTED_COLUMNS = {
    "categories.csv": ["category_id", "category_name"],
    "brands.csv": ["brand_id", "brand_name", "category_id"],
    "users.csv": [
        "user_id", "age", "gender", "city", "state",
        "account_created_date", "preferred_discount_min",
        "preferred_discount_max", "activity_level"
    ],
    "coupons.csv": [
        "coupon_id", "owner_id", "category_id", "brand_id",
        "discount_type", "discount_value", "minimum_purchase",
        "issue_date", "expiry_date", "coupon_value", "status",
        "city", "source", "transferable"
    ],
    "user_preferences.csv": [
        "preference_id", "user_id", "preferred_category_id",
        "preferred_brand_id", "minimum_discount", "preferred_city",
        "preferred_discount_type"
    ],
    "coupon_views.csv": [
        "view_id", "user_id", "coupon_id", "viewed_at", "view_duration_seconds"
    ],
    "coupon_requests.csv": [
        "request_id", "user_id", "coupon_id", "requested_at", "request_status"
    ],
    "coupon_usage.csv": [
        "usage_id", "user_id", "coupon_id", "used_at", "usage_status"
    ],
    "swaps.csv": [
        "swap_id", "proposer_id", "receiver_id", "offered_coupon_id",
        "requested_coupon_id", "proposed_at", "completed_at", "swap_status"
    ],
    "ratings.csv": [
        "rating_id", "swap_id", "rater_id", "rated_user_id",
        "rating", "review_text", "rated_at"
    ]
}


def run_validation():
    print("=" * 65)
    print("PHASE 3 - RAW DATASET INTEGRITY VALIDATION")
    print(f"Directory: {DATA_RAW_DIR}")
    print("=" * 65)

    all_passed = True
    test_count = 0
    pass_count = 0

    def check(name, condition, error_msg=""):
        nonlocal test_count, pass_count, all_passed
        test_count += 1
        if condition:
            print(f"[PASS] {name}")
            pass_count += 1
        else:
            print(f"[FAIL] {name} - {error_msg}")
            all_passed = False

    # 1. Check all 10 expected files exist
    missing_files = []
    for f in EXPECTED_FILES:
        path = os.path.join(DATA_RAW_DIR, f)
        if not os.path.isfile(path):
            missing_files.append(f)
    check("All 10 required CSV files exist", len(missing_files) == 0, f"Missing files: {missing_files}")

    if missing_files:
        print("\nAborting remaining checks due to missing files.")
        return False

    # Load datasets
    dfs = {}
    for f in EXPECTED_FILES:
        dfs[f] = pd.read_csv(os.path.join(DATA_RAW_DIR, f))

    # 2. Check required columns exist in each file
    col_errors = []
    for f, expected_cols in EXPECTED_COLUMNS.items():
        actual_cols = list(dfs[f].columns)
        missing_cols = [c for c in expected_cols if c not in actual_cols]
        if missing_cols:
            col_errors.append(f"{f} missing columns: {missing_cols}")
    check("Required columns present in all datasets", len(col_errors) == 0, "; ".join(col_errors))

    # 3. Check Primary ID uniqueness
    pk_checks = [
        ("categories.csv", "category_id"),
        ("brands.csv", "brand_id"),
        ("users.csv", "user_id"),
        ("coupons.csv", "coupon_id"),
        ("user_preferences.csv", "preference_id"),
        ("coupon_views.csv", "view_id"),
        ("coupon_requests.csv", "request_id"),
        ("coupon_usage.csv", "usage_id"),
        ("swaps.csv", "swap_id"),
        ("ratings.csv", "rating_id"),
    ]
    pk_duplicates = []
    for f, pk in pk_checks:
        if dfs[f][pk].duplicated().any():
            pk_duplicates.append(f"{f} has duplicate {pk}")
    check("Primary IDs are strictly unique", len(pk_duplicates) == 0, "; ".join(pk_duplicates))

    # 4. Check Foreign-Key References
    user_ids = set(dfs["users.csv"]["user_id"])
    category_ids = set(dfs["categories.csv"]["category_id"])
    brand_ids = set(dfs["brands.csv"]["brand_id"])
    coupon_ids = set(dfs["coupons.csv"]["coupon_id"])
    swap_ids = set(dfs["swaps.csv"]["swap_id"])

    # brands -> categories
    invalid_brand_cats = set(dfs["brands.csv"]["category_id"]) - category_ids
    check("brands.category_id -> categories.category_id", len(invalid_brand_cats) == 0, f"Invalid: {invalid_brand_cats}")

    # coupons -> users, categories, brands
    invalid_coupon_owners = set(dfs["coupons.csv"]["owner_id"]) - user_ids
    invalid_coupon_cats = set(dfs["coupons.csv"]["category_id"]) - category_ids
    invalid_coupon_brands = set(dfs["coupons.csv"]["brand_id"]) - brand_ids
    check("coupons FKs (owner_id, category_id, brand_id)",
          len(invalid_coupon_owners) == 0 and len(invalid_coupon_cats) == 0 and len(invalid_coupon_brands) == 0,
          f"Owner errs: {len(invalid_coupon_owners)}, Cat errs: {len(invalid_coupon_cats)}, Brand errs: {len(invalid_coupon_brands)}")

    # user_preferences -> users, categories, brands
    invalid_pref_users = set(dfs["user_preferences.csv"]["user_id"]) - user_ids
    invalid_pref_cats = set(dfs["user_preferences.csv"]["preferred_category_id"]) - category_ids
    invalid_pref_brands = set(dfs["user_preferences.csv"]["preferred_brand_id"]) - brand_ids
    check("user_preferences FKs (user_id, category_id, brand_id)",
          len(invalid_pref_users) == 0 and len(invalid_pref_cats) == 0 and len(invalid_pref_brands) == 0,
          f"User errs: {len(invalid_pref_users)}, Cat errs: {len(invalid_pref_cats)}, Brand errs: {len(invalid_pref_brands)}")

    # coupon_views -> users, coupons
    invalid_view_users = set(dfs["coupon_views.csv"]["user_id"]) - user_ids
    invalid_view_coupons = set(dfs["coupon_views.csv"]["coupon_id"]) - coupon_ids
    check("coupon_views FKs (user_id, coupon_id)",
          len(invalid_view_users) == 0 and len(invalid_view_coupons) == 0,
          f"User errs: {len(invalid_view_users)}, Coupon errs: {len(invalid_view_coupons)}")

    # coupon_requests -> users, coupons
    invalid_req_users = set(dfs["coupon_requests.csv"]["user_id"]) - user_ids
    invalid_req_coupons = set(dfs["coupon_requests.csv"]["coupon_id"]) - coupon_ids
    check("coupon_requests FKs (user_id, coupon_id)",
          len(invalid_req_users) == 0 and len(invalid_req_coupons) == 0,
          f"User errs: {len(invalid_req_users)}, Coupon errs: {len(invalid_req_coupons)}")

    # coupon_usage -> users, coupons
    invalid_use_users = set(dfs["coupon_usage.csv"]["user_id"]) - user_ids
    invalid_use_coupons = set(dfs["coupon_usage.csv"]["coupon_id"]) - coupon_ids
    check("coupon_usage FKs (user_id, coupon_id)",
          len(invalid_use_users) == 0 and len(invalid_use_coupons) == 0,
          f"User errs: {len(invalid_use_users)}, Coupon errs: {len(invalid_use_coupons)}")

    # swaps -> users, coupons
    invalid_swap_props = set(dfs["swaps.csv"]["proposer_id"]) - user_ids
    invalid_swap_recvs = set(dfs["swaps.csv"]["receiver_id"]) - user_ids
    invalid_swap_offered = set(dfs["swaps.csv"]["offered_coupon_id"]) - coupon_ids
    invalid_swap_req = set(dfs["swaps.csv"]["requested_coupon_id"]) - coupon_ids
    check("swaps FKs (proposer_id, receiver_id, offered_coupon_id, requested_coupon_id)",
          len(invalid_swap_props) == 0 and len(invalid_swap_recvs) == 0 and len(invalid_swap_offered) == 0 and len(invalid_swap_req) == 0,
          f"Props: {len(invalid_swap_props)}, Recvs: {len(invalid_swap_recvs)}, Offered: {len(invalid_swap_offered)}, Req: {len(invalid_swap_req)}")

    # ratings -> swaps, users
    invalid_rate_swaps = set(dfs["ratings.csv"]["swap_id"]) - swap_ids
    invalid_rate_raters = set(dfs["ratings.csv"]["rater_id"]) - user_ids
    invalid_rate_rated = set(dfs["ratings.csv"]["rated_user_id"]) - user_ids
    check("ratings FKs (swap_id, rater_id, rated_user_id)",
          len(invalid_rate_swaps) == 0 and len(invalid_rate_raters) == 0 and len(invalid_rate_rated) == 0,
          f"Swaps: {len(invalid_rate_swaps)}, Raters: {len(invalid_rate_raters)}, Rated: {len(invalid_rate_rated)}")

    # 5. Logical Constraints: Date validation
    coupons_df = dfs["coupons.csv"]
    date_invalid = (pd.to_datetime(coupons_df["expiry_date"]) < pd.to_datetime(coupons_df["issue_date"])).sum()
    check("Coupon expiry_date >= issue_date", date_invalid == 0, f"Found {date_invalid} coupons with expiry < issue")

    # 6. Logical Constraints: Coupon values positive
    neg_coupon_values = (coupons_df["coupon_value"] <= 0).sum()
    check("Coupon values are strictly positive (> 0)", neg_coupon_values == 0, f"Found {neg_coupon_values} non-positive values")

    # 7. Logical Constraints: Discount values valid
    neg_discount_values = (coupons_df["discount_value"] <= 0).sum()
    pct_over_100 = ((coupons_df["discount_type"] == "percentage") & (coupons_df["discount_value"] > 100)).sum()
    check("Coupon discount values are valid (> 0 and percentage <= 100)",
          neg_discount_values == 0 and pct_over_100 == 0,
          f"Non-positive: {neg_discount_values}, Over 100%: {pct_over_100}")

    # 8. Ratings: Scores within 1 to 5
    ratings_df = dfs["ratings.csv"]
    invalid_scores = (~ratings_df["rating"].between(1, 5)).sum()
    check("Rating scores are strictly within [1, 5]", invalid_scores == 0, f"Found {invalid_scores} out-of-range scores")

    # 9. Ratings: No self-ratings
    self_ratings = (ratings_df["rater_id"] == ratings_df["rated_user_id"]).sum()
    check("No self-ratings (rater_id != rated_user_id)", self_ratings == 0, f"Found {self_ratings} self-ratings")

    # 10. Swaps: Proposer != Receiver & Offered != Requested
    swaps_df = dfs["swaps.csv"]
    self_swaps = (swaps_df["proposer_id"] == swaps_df["receiver_id"]).sum()
    same_coupons = (swaps_df["offered_coupon_id"] == swaps_df["requested_coupon_id"]).sum()
    check("Swaps logical integrity (proposer != receiver and offered != requested)",
          self_swaps == 0 and same_coupons == 0,
          f"Self swaps: {self_swaps}, Same coupons: {same_coupons}")

    # 11. Controlled categorical values
    valid_categories = {
        "users.csv": {
            "gender": {"Male", "Female", "Other"},
            "activity_level": {"low", "medium", "high"}
        },
        "coupons.csv": {
            "discount_type": {"percentage", "flat"},
            "status": {"available", "claimed", "expired", "swapped"},
            "source": {"purchased", "gifted", "earned", "referral"},
            "transferable": {"yes", "no"}
        },
        "coupon_requests.csv": {
            "request_status": {"pending", "accepted", "rejected", "cancelled"}
        },
        "coupon_usage.csv": {
            "usage_status": {"used", "expired", "cancelled"}
        },
        "swaps.csv": {
            "swap_status": {"proposed", "accepted", "rejected", "completed", "cancelled"}
        }
    }
    cat_errors = []
    for file_name, col_dict in valid_categories.items():
        df = dfs[file_name]
        for col, allowed_vals in col_dict.items():
            actual_vals = set(df[col].dropna().unique())
            disallowed = actual_vals - allowed_vals
            if disallowed:
                cat_errors.append(f"{file_name} [{col}] has invalid values: {disallowed}")
    check("Categorical columns use valid controlled vocabularies", len(cat_errors) == 0, "; ".join(cat_errors))

    print("=" * 65)
    print(f"RESULTS: {pass_count}/{test_count} validation checks passed.")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)

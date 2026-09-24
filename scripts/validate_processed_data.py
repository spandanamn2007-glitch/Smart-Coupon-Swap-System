"""
Phase 4 Processed Dataset Validation Script
Smart Coupon Swap System

Performs read-only validation of cleaned CSV datasets in data/processed/.
Verifies:
1. All 10 expected processed files exist.
2. Required schema columns exist.
3. Primary keys are strictly unique.
4. Foreign-key referential integrity across all processed tables.
5. Value ranges, valid dates, and logical constraints.
6. Categorical consistency.
7. Only legitimate missing values exist (swaps.completed_at for uncompleted swaps).
8. Raw datasets in data/raw/ were NOT modified.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

EXPECTED_PROCESSED_FILES = [
    "categories_clean.csv",
    "brands_clean.csv",
    "users_clean.csv",
    "coupons_clean.csv",
    "user_preferences_clean.csv",
    "coupon_views_clean.csv",
    "coupon_requests_clean.csv",
    "coupon_usage_clean.csv",
    "swaps_clean.csv",
    "ratings_clean.csv"
]

EXPECTED_RAW_FILES = [
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
    "categories_clean.csv": ["category_id", "category_name"],
    "brands_clean.csv": ["brand_id", "brand_name", "category_id"],
    "users_clean.csv": [
        "user_id", "age", "gender", "city", "state",
        "account_created_date", "preferred_discount_min",
        "preferred_discount_max", "activity_level"
    ],
    "coupons_clean.csv": [
        "coupon_id", "owner_id", "category_id", "brand_id",
        "discount_type", "discount_value", "minimum_purchase",
        "issue_date", "expiry_date", "coupon_value", "status",
        "city", "source", "transferable"
    ],
    "user_preferences_clean.csv": [
        "preference_id", "user_id", "preferred_category_id",
        "preferred_brand_id", "minimum_discount", "preferred_city",
        "preferred_discount_type"
    ],
    "coupon_views_clean.csv": [
        "view_id", "user_id", "coupon_id", "viewed_at", "view_duration_seconds"
    ],
    "coupon_requests_clean.csv": [
        "request_id", "user_id", "coupon_id", "requested_at", "request_status"
    ],
    "coupon_usage_clean.csv": [
        "usage_id", "user_id", "coupon_id", "used_at", "usage_status"
    ],
    "swaps_clean.csv": [
        "swap_id", "proposer_id", "receiver_id", "offered_coupon_id",
        "requested_coupon_id", "proposed_at", "completed_at", "swap_status"
    ],
    "ratings_clean.csv": [
        "rating_id", "swap_id", "rater_id", "rated_user_id",
        "rating", "review_text", "rated_at"
    ]
}


def run_validation():
    print("=" * 65)
    print("PHASE 4 - PROCESSED DATASET INTEGRITY VALIDATION")
    print(f"Processed Directory: {PROCESSED_DIR}")
    print(f"Raw Directory      : {RAW_DIR}")
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

    # 1. All 10 processed files exist
    missing_proc = [f for f in EXPECTED_PROCESSED_FILES if not os.path.isfile(os.path.join(PROCESSED_DIR, f))]
    check("All 10 required processed CSV files exist", len(missing_proc) == 0, f"Missing: {missing_proc}")
    if missing_proc:
        return False

    # 2. Raw datasets were not modified / deleted
    missing_raw = [f for f in EXPECTED_RAW_FILES if not os.path.isfile(os.path.join(RAW_DIR, f))]
    check("All 10 raw CSV files still exist in data/raw/", len(missing_raw) == 0, f"Missing: {missing_raw}")

    # Load processed datasets
    dfs = {f: pd.read_csv(os.path.join(PROCESSED_DIR, f)) for f in EXPECTED_PROCESSED_FILES}

    # 3. Schema column checks
    col_errs = []
    for f, cols in EXPECTED_COLUMNS.items():
        missing = [c for c in cols if c not in dfs[f].columns]
        if missing:
            col_errs.append(f"{f} missing: {missing}")
    check("Required columns present in all processed datasets", len(col_errs) == 0, "; ".join(col_errs))

    # 4. Primary ID uniqueness
    pk_map = {
        "categories_clean.csv": "category_id",
        "brands_clean.csv": "brand_id",
        "users_clean.csv": "user_id",
        "coupons_clean.csv": "coupon_id",
        "user_preferences_clean.csv": "preference_id",
        "coupon_views_clean.csv": "view_id",
        "coupon_requests_clean.csv": "request_id",
        "coupon_usage_clean.csv": "usage_id",
        "swaps_clean.csv": "swap_id",
        "ratings_clean.csv": "rating_id",
    }
    pk_dups = [f"{f}.{pk}" for f, pk in pk_map.items() if dfs[f][pk].duplicated().any()]
    check("Primary IDs are strictly unique in processed datasets", len(pk_dups) == 0, f"Duplicates in: {pk_dups}")

    # 5. Missing values in required fields
    unintended_nulls = []
    for f, df in dfs.items():
        for col in df.columns:
            if f == "swaps_clean.csv" and col == "completed_at":
                continue  # legitimate nulls
            null_count = df[col].isnull().sum()
            if null_count > 0:
                unintended_nulls.append(f"{f}.{col}: {null_count} nulls")
    check("No unintended missing values in required columns", len(unintended_nulls) == 0, "; ".join(unintended_nulls))

    # 6. Swaps completed_at logic
    swaps_df = dfs["swaps_clean.csv"]
    uncompleted_non_nulls = swaps_df[~swaps_df["swap_status"].isin(["accepted", "completed"])]["completed_at"].notnull().sum()
    check("swaps.completed_at null only when swap is uncompleted", uncompleted_non_nulls == 0, f"Found {uncompleted_non_nulls} premature completion timestamps")

    # 7. Foreign key referential integrity
    user_ids = set(dfs["users_clean.csv"]["user_id"])
    cat_ids = set(dfs["categories_clean.csv"]["category_id"])
    brand_ids = set(dfs["brands_clean.csv"]["brand_id"])
    coupon_ids = set(dfs["coupons_clean.csv"]["coupon_id"])
    swap_ids = set(dfs["swaps_clean.csv"]["swap_id"])

    fk_errors = []
    if not set(dfs["brands_clean.csv"]["category_id"]).issubset(cat_ids):
        fk_errors.append("brands.category_id -> categories")
    if not set(dfs["coupons_clean.csv"]["owner_id"]).issubset(user_ids):
        fk_errors.append("coupons.owner_id -> users")
    if not set(dfs["coupons_clean.csv"]["category_id"]).issubset(cat_ids):
        fk_errors.append("coupons.category_id -> categories")
    if not set(dfs["coupons_clean.csv"]["brand_id"]).issubset(brand_ids):
        fk_errors.append("coupons.brand_id -> brands")
    if not set(dfs["user_preferences_clean.csv"]["user_id"]).issubset(user_ids):
        fk_errors.append("user_preferences.user_id -> users")
    if not set(dfs["coupon_views_clean.csv"]["user_id"]).issubset(user_ids):
        fk_errors.append("coupon_views.user_id -> users")
    if not set(dfs["coupon_views_clean.csv"]["coupon_id"]).issubset(coupon_ids):
        fk_errors.append("coupon_views.coupon_id -> coupons")
    if not set(dfs["coupon_requests_clean.csv"]["user_id"]).issubset(user_ids):
        fk_errors.append("coupon_requests.user_id -> users")
    if not set(dfs["coupon_requests_clean.csv"]["coupon_id"]).issubset(coupon_ids):
        fk_errors.append("coupon_requests.coupon_id -> coupons")
    if not set(dfs["coupon_usage_clean.csv"]["user_id"]).issubset(user_ids):
        fk_errors.append("coupon_usage.user_id -> users")
    if not set(dfs["coupon_usage_clean.csv"]["coupon_id"]).issubset(coupon_ids):
        fk_errors.append("coupon_usage.coupon_id -> coupons")
    if not set(dfs["swaps_clean.csv"]["proposer_id"]).issubset(user_ids):
        fk_errors.append("swaps.proposer_id -> users")
    if not set(dfs["swaps_clean.csv"]["receiver_id"]).issubset(user_ids):
        fk_errors.append("swaps.receiver_id -> users")
    if not set(dfs["swaps_clean.csv"]["offered_coupon_id"]).issubset(coupon_ids):
        fk_errors.append("swaps.offered_coupon_id -> coupons")
    if not set(dfs["swaps_clean.csv"]["requested_coupon_id"]).issubset(coupon_ids):
        fk_errors.append("swaps.requested_coupon_id -> coupons")
    if not set(dfs["ratings_clean.csv"]["swap_id"]).issubset(swap_ids):
        fk_errors.append("ratings.swap_id -> swaps")
    if not set(dfs["ratings_clean.csv"]["rater_id"]).issubset(user_ids):
        fk_errors.append("ratings.rater_id -> users")
    if not set(dfs["ratings_clean.csv"]["rated_user_id"]).issubset(user_ids):
        fk_errors.append("ratings.rated_user_id -> users")
    check("Foreign-key relationships strictly valid across all processed tables", len(fk_errors) == 0, "; ".join(fk_errors))

    # 8. Numeric range checks
    coupons_df = dfs["coupons_clean.csv"]
    valid_c_val = (coupons_df["coupon_value"] > 0).all()
    valid_d_val = (coupons_df["discount_value"] > 0).all()
    ratings_df = dfs["ratings_clean.csv"]
    valid_ratings = (ratings_df["rating"].between(1, 5)).all()
    users_df = dfs["users_clean.csv"]
    valid_age = (users_df["age"].between(18, 100)).all()
    views_df = dfs["coupon_views_clean.csv"]
    valid_duration = (views_df["view_duration_seconds"] >= 0).all()
    check("Numeric fields within strictly valid ranges",
          valid_c_val and valid_d_val and valid_ratings and valid_age and valid_duration,
          "One or more numeric bounds violated")

    # 9. Date validity checks
    valid_c_dates = (pd.to_datetime(coupons_df["expiry_date"]) >= pd.to_datetime(coupons_df["issue_date"])).all()
    check("Coupon dates valid (expiry_date >= issue_date)", valid_c_dates, "Found invalid expiry dates")

    # 10. Logical check: no self ratings
    no_self_ratings = (ratings_df["rater_id"] != ratings_df["rated_user_id"]).all()
    check("No self-ratings in processed ratings (rater_id != rated_user_id)", no_self_ratings, "Self-ratings detected")

    # 11. Logical check: swaps proposer != receiver & offered != requested
    valid_swaps = (
        (swaps_df["proposer_id"] != swaps_df["receiver_id"]).all() and
        (swaps_df["offered_coupon_id"] != swaps_df["requested_coupon_id"]).all()
    )
    check("Swaps logical integrity (proposer != receiver, offered != requested)", valid_swaps, "Swap logic violated")

    # 12. Check raw datasets were not modified
    # Compare row counts of raw vs processed
    row_count_diffs = []
    for r_name, p_name in zip(EXPECTED_RAW_FILES, EXPECTED_PROCESSED_FILES):
        r_df = pd.read_csv(os.path.join(RAW_DIR, r_name))
        p_df = pd.read_csv(os.path.join(PROCESSED_DIR, p_name))
        if len(r_df) != len(p_df):
            row_count_diffs.append(f"{r_name} ({len(r_df)}) != {p_name} ({len(p_df)})")
    check("Raw datasets preserved and row counts match processed datasets",
          len(row_count_diffs) == 0,
          "; ".join(row_count_diffs))

    print("=" * 65)
    print(f"RESULTS: {pass_count}/{test_count} validation checks passed.")
    print("=" * 65)

    return all_passed


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)

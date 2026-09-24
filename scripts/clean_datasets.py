"""
Phase 4 Dataset Cleaning & Preprocessing Script
Smart Coupon Swap System

Reads synthetic raw CSV files from data/raw/, applies quality checks,
cleans, standardizes data types, formats dates, validates constraints,
and outputs clean datasets to data/processed/*_clean.csv.

Crucial Rule: Raw files in data/raw/ are NEVER modified.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

TABLE_MAPPING = {
    "categories.csv": "categories_clean.csv",
    "brands.csv": "brands_clean.csv",
    "users.csv": "users_clean.csv",
    "coupons.csv": "coupons_clean.csv",
    "user_preferences.csv": "user_preferences_clean.csv",
    "coupon_views.csv": "coupon_views_clean.csv",
    "coupon_requests.csv": "coupon_requests_clean.csv",
    "coupon_usage.csv": "coupon_usage_clean.csv",
    "swaps.csv": "swaps_clean.csv",
    "ratings.csv": "ratings_clean.csv",
}


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strips leading/trailing whitespace on all string columns."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def clean_categories(raw_path: str) -> pd.DataFrame:
    print("Processing categories...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["category_id"])
    df["category_id"] = df["category_id"].astype(str)
    df["category_name"] = df["category_name"].astype(str)
    return df


def clean_brands(raw_path: str, valid_categories: set) -> pd.DataFrame:
    print("Processing brands...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["brand_id"])
    # Validate FK
    invalid = ~df["category_id"].isin(valid_categories)
    if invalid.any():
        print(f"  Warning: Removing {invalid.sum()} brands with invalid category_id")
        df = df[~invalid]
    df["brand_id"] = df["brand_id"].astype(str)
    df["brand_name"] = df["brand_name"].astype(str)
    df["category_id"] = df["category_id"].astype(str)
    return df


def clean_users(raw_path: str) -> pd.DataFrame:
    print("Processing users...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["user_id"])
    df["age"] = df["age"].astype(int)
    df["account_created_date"] = pd.to_datetime(df["account_created_date"]).dt.strftime("%Y-%m-%d")
    df["preferred_discount_min"] = df["preferred_discount_min"].astype(int)
    df["preferred_discount_max"] = df["preferred_discount_max"].astype(int)
    # Validate preference min <= max
    invalid_pref = df["preferred_discount_min"] > df["preferred_discount_max"]
    if invalid_pref.any():
        print(f"  Warning: Correcting {invalid_pref.sum()} user preference bounds")
        df.loc[invalid_pref, "preferred_discount_max"] = df.loc[invalid_pref, "preferred_discount_min"]
    return df


def clean_coupons(raw_path: str, valid_users: set, valid_categories: set, valid_brands: set) -> pd.DataFrame:
    print("Processing coupons...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["coupon_id"])
    
    # FK validation
    valid_mask = (
        df["owner_id"].isin(valid_users) &
        df["category_id"].isin(valid_categories) &
        df["brand_id"].isin(valid_brands)
    )
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} coupons with broken FKs")
        df = df[valid_mask]
        
    # Standardize dates
    df["issue_date"] = pd.to_datetime(df["issue_date"]).dt.strftime("%Y-%m-%d")
    df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.strftime("%Y-%m-%d")
    
    # Ensure expiry >= issue
    invalid_dates = pd.to_datetime(df["expiry_date"]) < pd.to_datetime(df["issue_date"])
    if invalid_dates.any():
        print(f"  Warning: Removing {invalid_dates.sum()} coupons with expiry < issue")
        df = df[~invalid_dates]
        
    df["discount_value"] = df["discount_value"].astype(float).round(2)
    df["minimum_purchase"] = df["minimum_purchase"].astype(int)
    df["coupon_value"] = df["coupon_value"].astype(float).round(2)
    df["transferable"] = df["transferable"].str.lower()
    df["discount_type"] = df["discount_type"].str.lower()
    df["status"] = df["status"].str.lower()
    df["source"] = df["source"].str.lower()
    return df


def clean_user_preferences(raw_path: str, valid_users: set, valid_categories: set, valid_brands: set) -> pd.DataFrame:
    print("Processing user_preferences...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["preference_id"])
    valid_mask = (
        df["user_id"].isin(valid_users) &
        df["preferred_category_id"].isin(valid_categories) &
        df["preferred_brand_id"].isin(valid_brands)
    )
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} preferences with broken FKs")
        df = df[valid_mask]
    df["minimum_discount"] = df["minimum_discount"].astype(int)
    df["preferred_discount_type"] = df["preferred_discount_type"].str.lower()
    return df


def clean_coupon_views(raw_path: str, valid_users: set, valid_coupons: set) -> pd.DataFrame:
    print("Processing coupon_views...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["view_id"])
    valid_mask = df["user_id"].isin(valid_users) & df["coupon_id"].isin(valid_coupons)
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} views with broken FKs")
        df = df[valid_mask]
    df["viewed_at"] = pd.to_datetime(df["viewed_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["view_duration_seconds"] = df["view_duration_seconds"].astype(int)
    return df


def clean_coupon_requests(raw_path: str, valid_users: set, valid_coupons: set) -> pd.DataFrame:
    print("Processing coupon_requests...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["request_id"])
    valid_mask = df["user_id"].isin(valid_users) & df["coupon_id"].isin(valid_coupons)
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} requests with broken FKs")
        df = df[valid_mask]
    df["requested_at"] = pd.to_datetime(df["requested_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["request_status"] = df["request_status"].str.lower()
    return df


def clean_coupon_usage(raw_path: str, valid_users: set, valid_coupons: set) -> pd.DataFrame:
    print("Processing coupon_usage...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["usage_id"])
    valid_mask = df["user_id"].isin(valid_users) & df["coupon_id"].isin(valid_coupons)
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} usage records with broken FKs")
        df = df[valid_mask]
    df["used_at"] = pd.to_datetime(df["used_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["usage_status"] = df["usage_status"].str.lower()
    return df


def clean_swaps(raw_path: str, valid_users: set, valid_coupons: set) -> pd.DataFrame:
    print("Processing swaps...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["swap_id"])
    
    # Logical check: proposer != receiver, offered != requested
    valid_mask = (
        df["proposer_id"].isin(valid_users) &
        df["receiver_id"].isin(valid_users) &
        df["offered_coupon_id"].isin(valid_coupons) &
        df["requested_coupon_id"].isin(valid_coupons) &
        (df["proposer_id"] != df["receiver_id"]) &
        (df["offered_coupon_id"] != df["requested_coupon_id"])
    )
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} invalid swaps")
        df = df[valid_mask]
        
    df["proposed_at"] = pd.to_datetime(df["proposed_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    # completed_at can be null for proposed/rejected/cancelled
    df["completed_at"] = pd.to_datetime(df["completed_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["swap_status"] = df["swap_status"].str.lower()
    return df


def clean_ratings(raw_path: str, valid_swaps: set, valid_users: set) -> pd.DataFrame:
    print("Processing ratings...")
    df = pd.read_csv(raw_path)
    df = clean_string_columns(df)
    df = df.drop_duplicates(subset=["rating_id"])
    valid_mask = (
        df["swap_id"].isin(valid_swaps) &
        df["rater_id"].isin(valid_users) &
        df["rated_user_id"].isin(valid_users) &
        (df["rater_id"] != df["rated_user_id"])
    )
    if (~valid_mask).any():
        print(f"  Warning: Removing {(~valid_mask).sum()} invalid ratings")
        df = df[valid_mask]
    df["rating"] = df["rating"].astype(int)
    df["rated_at"] = pd.to_datetime(df["rated_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def main():
    print("=" * 65)
    print("PHASE 4 - DATA CLEANING & PREPROCESSING")
    print(f"Source Directory: {RAW_DIR}")
    print(f"Target Directory: {PROCESSED_DIR}")
    print("=" * 65)

    # 1. Categories
    cats_df = clean_categories(os.path.join(RAW_DIR, "categories.csv"))
    valid_cats = set(cats_df["category_id"])

    # 2. Brands
    brands_df = clean_brands(os.path.join(RAW_DIR, "brands.csv"), valid_cats)
    valid_brands = set(brands_df["brand_id"])

    # 3. Users
    users_df = clean_users(os.path.join(RAW_DIR, "users.csv"))
    valid_users = set(users_df["user_id"])

    # 4. Coupons
    coupons_df = clean_coupons(os.path.join(RAW_DIR, "coupons.csv"), valid_users, valid_cats, valid_brands)
    valid_coupons = set(coupons_df["coupon_id"])

    # 5. User Preferences
    prefs_df = clean_user_preferences(os.path.join(RAW_DIR, "user_preferences.csv"), valid_users, valid_cats, valid_brands)

    # 6. Coupon Views
    views_df = clean_coupon_views(os.path.join(RAW_DIR, "coupon_views.csv"), valid_users, valid_coupons)

    # 7. Coupon Requests
    requests_df = clean_coupon_requests(os.path.join(RAW_DIR, "coupon_requests.csv"), valid_users, valid_coupons)

    # 8. Coupon Usage
    usage_df = clean_coupon_usage(os.path.join(RAW_DIR, "coupon_usage.csv"), valid_users, valid_coupons)

    # 9. Swaps
    swaps_df = clean_swaps(os.path.join(RAW_DIR, "swaps.csv"), valid_users, valid_coupons)
    valid_swaps = set(swaps_df["swap_id"])

    # 10. Ratings
    ratings_df = clean_ratings(os.path.join(RAW_DIR, "ratings.csv"), valid_swaps, valid_users)

    # Save all processed datasets
    data_dict = {
        "categories_clean.csv": cats_df,
        "brands_clean.csv": brands_df,
        "users_clean.csv": users_df,
        "coupons_clean.csv": coupons_df,
        "user_preferences_clean.csv": prefs_df,
        "coupon_views_clean.csv": views_df,
        "coupon_requests_clean.csv": requests_df,
        "coupon_usage_clean.csv": usage_df,
        "swaps_clean.csv": swaps_df,
        "ratings_clean.csv": ratings_df,
    }

    print("\nWriting cleaned datasets to data/processed/:")
    for fname, df in data_dict.items():
        out_path = os.path.join(PROCESSED_DIR, fname)
        df.to_csv(out_path, index=False)
        print(f"  [OK] {fname:<30} {len(df):>6} rows, {len(df.columns):>2} cols")

    print("=" * 65)
    print("Data cleaning completed successfully. All raw datasets preserved.")
    print("=" * 65)


if __name__ == "__main__":
    main()


"""
Phase 5 - Exploratory Data Analysis (EDA) Script
Smart Coupon Swap System

Performs rigorous exploratory analysis on cleaned/processed datasets in data/processed/.
Generates statistical summaries, detects outliers, analyzes temporal trends,
computes correlations, and exports high-resolution visual plots to outputs/eda/.

Strict Rule: Does not perform feature engineering, ML, predictions, or backend tasks.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.titlesize": 16
})

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "eda")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_datasets():
    print("Loading processed datasets...")
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
    for name, fname in files.items():
        p = os.path.join(DATA_DIR, fname)
        dfs[name] = pd.read_csv(p)
        print(f"  Loaded {name:<18}: {len(dfs[name]):>6} rows, {len(dfs[name].columns):>2} cols")
    return dfs


def analyze_and_plot(dfs):
    stats = {}

    # ==========================================
    # 1. Categories & Brands
    # ==========================================
    print("\n--- 1. Categories & Brands Analysis ---")
    cats = dfs["categories"]
    brands = dfs["brands"]
    coupons = dfs["coupons"]

    brands_per_cat = brands.groupby("category_id").size().reset_index(name="brand_count")
    brands_per_cat = brands_per_cat.merge(cats, on="category_id").sort_values(by="brand_count", ascending=False)
    
    coupons_per_cat = coupons.groupby("category_id").size().reset_index(name="coupon_count")
    coupons_per_cat = coupons_per_cat.merge(cats, on="category_id").sort_values(by="coupon_count", ascending=False)

    stats["categories_count"] = len(cats)
    stats["brands_count"] = len(brands)
    stats["coupons_per_cat"] = dict(zip(coupons_per_cat["category_name"], coupons_per_cat["coupon_count"]))
    stats["brands_per_cat"] = dict(zip(brands_per_cat["category_name"], brands_per_cat["brand_count"]))

    # Plot 1: Coupons per Category
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=coupons_per_cat, x="category_name", y="coupon_count", color="#3b82f6")
    plt.title("Coupon Distribution Across Categories")
    plt.xlabel("Category")
    plt.ylabel("Number of Coupons")
    plt.xticks(rotation=45, ha="right")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="baseline", fontsize=10, xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "01_category_coupon_distribution.png"), dpi=300)
    plt.close()

    # Plot 2: Brands per Category
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(data=brands_per_cat, x="category_name", y="brand_count", color="#10b981")
    plt.title("Brand Representation by Category")
    plt.xlabel("Category")
    plt.ylabel("Number of Brands")
    plt.xticks(rotation=45, ha="right")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="baseline", fontsize=10, xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "02_brands_per_category.png"), dpi=300)
    plt.close()

    # ==========================================
    # 2. Users Demographics & Preferences
    # ==========================================
    print("\n--- 2. Users Analysis ---")
    users = dfs["users"]

    # Numerical statistics
    age_desc = users["age"].describe().to_dict()
    disc_min_desc = users["preferred_discount_min"].describe().to_dict()
    disc_max_desc = users["preferred_discount_max"].describe().to_dict()
    stats["user_age"] = age_desc
    stats["user_pref_min"] = disc_min_desc
    stats["user_pref_max"] = disc_max_desc

    # Outlier detection for user age using IQR
    q1 = users["age"].quantile(0.25)
    q3 = users["age"].quantile(0.75)
    iqr = q3 - q1
    age_outliers = users[(users["age"] < q1 - 1.5 * iqr) | (users["age"] > q3 + 1.5 * iqr)]
    stats["user_age_outliers_count"] = len(age_outliers)

    # Gender breakdown
    gender_counts = users["gender"].value_counts().to_dict()
    activity_counts = users["activity_level"].value_counts().to_dict()
    stats["user_gender_breakdown"] = gender_counts
    stats["user_activity_breakdown"] = activity_counts

    # Plot 3: User Age Distribution
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(users["age"], bins=20, kde=True, ax=axes[0], color="#6366f1")
    axes[0].set_title("User Age Histogram with KDE")
    axes[0].set_xlabel("Age")
    axes[0].set_ylabel("Count")

    sns.boxplot(y=users["age"], ax=axes[1], color="#a5b4fc")
    axes[1].set_title("User Age Boxplot (Outlier Check)")
    axes[1].set_ylabel("Age")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "03_user_age_distribution.png"), dpi=300)
    plt.close()

    # Plot 4: User Geographic Distribution (Top Cities)
    top_cities = users["city"].value_counts().reset_index()
    top_cities.columns = ["city", "count"]
    plt.figure(figsize=(12, 5))
    ax = sns.barplot(data=top_cities, x="city", y="count", color="#8b5cf6")
    plt.title("Geographic Distribution of Users Across Cities")
    plt.xlabel("City")
    plt.ylabel("Registered Users")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "04_user_geographic_distribution.png"), dpi=300)
    plt.close()

    # Plot 5: User Activity by Gender
    plt.figure(figsize=(8, 5))
    sns.countplot(data=users, x="activity_level", hue="gender", order=["low", "medium", "high"])
    plt.title("User Activity Levels Segmented by Gender")
    plt.xlabel("Activity Level")
    plt.ylabel("Number of Users")
    plt.legend(title="Gender")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "05_user_activity_and_gender.png"), dpi=300)
    plt.close()

    # ==========================================
    # 3. Coupons Analysis
    # ==========================================
    print("\n--- 3. Coupons Analysis ---")
    c_val_desc = coupons["coupon_value"].describe().to_dict()
    d_val_desc = coupons["discount_value"].describe().to_dict()
    min_p_desc = coupons["minimum_purchase"].describe().to_dict()
    stats["coupon_value"] = c_val_desc
    stats["discount_value"] = d_val_desc
    stats["minimum_purchase"] = min_p_desc

    # Outliers in coupon_value
    c_q1 = coupons["coupon_value"].quantile(0.25)
    c_q3 = coupons["coupon_value"].quantile(0.75)
    c_iqr = c_q3 - c_q1
    c_val_outliers = coupons[(coupons["coupon_value"] < c_q1 - 1.5 * c_iqr) | (coupons["coupon_value"] > c_q3 + 1.5 * c_iqr)]
    stats["coupon_val_outliers_count"] = len(c_val_outliers)

    # Validity duration in days
    coupons_temp = coupons.copy()
    coupons_temp["validity_days"] = (pd.to_datetime(coupons_temp["expiry_date"]) - pd.to_datetime(coupons_temp["issue_date"])).dt.days
    validity_desc = coupons_temp["validity_days"].describe().to_dict()
    stats["validity_days"] = validity_desc

    # Plot 6: Coupon Value & Discount Value Distributions
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.boxplot(data=coupons, y="coupon_value", ax=axes[0], color="#ec4899")
    axes[0].set_title("Coupon Value Boxplot")
    axes[0].set_ylabel("Value (Currency Units)")

    sns.histplot(data=coupons, x="coupon_value", bins=30, kde=True, ax=axes[1], color="#f43f5e")
    axes[1].set_title("Coupon Value Distribution")
    axes[1].set_xlabel("Value (Currency Units)")
    axes[1].set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "06_coupon_value_distribution.png"), dpi=300)
    plt.close()

    # Plot 7: Discount Type & Status Breakdown
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.countplot(data=coupons, x="discount_type", ax=axes[0], palette="Blues_d", hue="discount_type", legend=False)
    axes[0].set_title("Discount Type Breakdown")
    axes[0].set_xlabel("Discount Type")
    axes[0].set_ylabel("Count")

    sns.countplot(data=coupons, x="status", ax=axes[1], palette="Greens_d", hue="status", legend=False)
    axes[1].set_title("Coupon Status Breakdown")
    axes[1].set_xlabel("Listing Status")
    axes[1].set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "07_coupon_type_and_status.png"), dpi=300)
    plt.close()

    # Plot 8: Coupon Validity Duration
    plt.figure(figsize=(10, 5))
    sns.histplot(coupons_temp["validity_days"], bins=25, kde=True, color="#0ea5e9")
    plt.title("Distribution of Coupon Validity Duration (Days)")
    plt.xlabel("Validity Period (Days from Issue to Expiry)")
    plt.ylabel("Number of Coupons")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "08_coupon_validity_duration.png"), dpi=300)
    plt.close()

    # ==========================================
    # 4. Activity Telemetry (Views, Requests, Usage)
    # ==========================================
    print("\n--- 4. User Activity Telemetry ---")
    views = dfs["coupon_views"]
    requests = dfs["coupon_requests"]
    usage = dfs["coupon_usage"]

    stats["total_views"] = len(views)
    stats["total_requests"] = len(requests)
    stats["total_usage"] = len(usage)
    stats["view_duration_stats"] = views["view_duration_seconds"].describe().to_dict()
    stats["request_status_counts"] = requests["request_status"].value_counts().to_dict()
    stats["usage_status_counts"] = usage["usage_status"].value_counts().to_dict()

    # Plot 9: Activity Funnel Volume
    funnel_df = pd.DataFrame({
        "Stage": ["Views", "Requests", "Usage"],
        "Count": [len(views), len(requests), len(usage)]
    })
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(data=funnel_df, x="Stage", y="Count", palette=["#3b82f6", "#f59e0b", "#10b981"], hue="Stage", legend=False)
    plt.title("User Interaction Funnel (Volume Comparison)")
    plt.xlabel("Interaction Stage")
    plt.ylabel("Total Records")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="baseline", fontsize=11, xytext=(0, 4), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "09_user_engagement_funnel.png"), dpi=300)
    plt.close()

    # Plot 10: View Duration Distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(views["view_duration_seconds"], bins=30, kde=True, color="#8b5cf6")
    plt.title("Distribution of Coupon View Dwell Time")
    plt.xlabel("View Duration (Seconds)")
    plt.ylabel("Number of Views")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "10_view_duration_distribution.png"), dpi=300)
    plt.close()

    # ==========================================
    # 5. Swaps Analysis
    # ==========================================
    print("\n--- 5. Swaps Analysis ---")
    swaps = dfs["swaps"]
    swap_status_counts = swaps["swap_status"].value_counts().to_dict()
    stats["swap_status_counts"] = swap_status_counts

    # Calculate turnaround hours for completed/accepted swaps
    comp_swaps = swaps[swaps["completed_at"].notnull()].copy()
    comp_swaps["turnaround_hours"] = (
        pd.to_datetime(comp_swaps["completed_at"]) - pd.to_datetime(comp_swaps["proposed_at"])
    ).dt.total_seconds() / 3600.0
    turnaround_desc = comp_swaps["turnaround_hours"].describe().to_dict()
    stats["swap_turnaround_hours"] = turnaround_desc

    # Monthly swap proposals
    swaps_temp = swaps.copy()
    swaps_temp["year_month"] = pd.to_datetime(swaps_temp["proposed_at"]).dt.to_period("M").astype(str)
    monthly_swaps = swaps_temp.groupby("year_month").size().reset_index(name="swap_count")

    # Plot 11: Swap Status Distribution
    plt.figure(figsize=(8, 5))
    ax = sns.barplot(x=list(swap_status_counts.keys()), y=list(swap_status_counts.values()), palette="viridis", hue=list(swap_status_counts.keys()), legend=False)
    plt.title("Swap Proposal Outcome Distribution")
    plt.xlabel("Swap Status")
    plt.ylabel("Count")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="baseline", fontsize=10, xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "11_swap_status_distribution.png"), dpi=300)
    plt.close()

    # Plot 12: Monthly Swap Trend
    plt.figure(figsize=(12, 5))
    sns.lineplot(data=monthly_swaps, x="year_month", y="swap_count", marker="o", color="#d97706", linewidth=2.5)
    plt.title("Monthly Swap Proposal Volume (2023 - 2025)")
    plt.xlabel("Month")
    plt.ylabel("Proposals")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "12_monthly_swap_proposals.png"), dpi=300)
    plt.close()

    # Plot 13: Turnaround time distribution
    plt.figure(figsize=(10, 5))
    sns.histplot(comp_swaps["turnaround_hours"], bins=20, kde=True, color="#059669")
    plt.title("Swap Resolution Turnaround Time (Hours)")
    plt.xlabel("Hours Between Proposal and Settlement")
    plt.ylabel("Completed Swaps")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "13_swap_turnaround_time.png"), dpi=300)
    plt.close()

    # ==========================================
    # 6. Ratings Analysis
    # ==========================================
    print("\n--- 6. Ratings Analysis ---")
    ratings = dfs["ratings"]
    rating_desc = ratings["rating"].describe().to_dict()
    rating_dist = ratings["rating"].value_counts().sort_index().to_dict()
    stats["rating_stats"] = rating_desc
    stats["rating_distribution"] = rating_dist

    # Plot 14: Rating Distribution
    plt.figure(figsize=(8, 5))
    ax = sns.countplot(data=ratings, x="rating", palette="YlOrRd", hue="rating", legend=False)
    plt.title("Counterparty Rating Score Frequencies (1 - 5 Stars)")
    plt.xlabel("Rating Score")
    plt.ylabel("Count")
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="baseline", fontsize=10, xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "14_rating_distribution.png"), dpi=300)
    plt.close()

    # ==========================================
    # 7. Cross-Dataset Correlation Analysis
    # ==========================================
    print("\n--- 7. Cross-Dataset Correlation Matrix ---")
    # Build a joined numerical table for meaningful correlations
    # coupons + views count + requests count
    c_views = views.groupby("coupon_id").size().reset_index(name="view_count")
    c_reqs = requests.groupby("coupon_id").size().reset_index(name="req_count")
    c_usage = usage.groupby("coupon_id").size().reset_index(name="usage_count")

    coupon_stats = coupons[["coupon_id", "discount_value", "minimum_purchase", "coupon_value"]].copy()
    coupon_stats = coupon_stats.merge(c_views, on="coupon_id", how="left").fillna(0)
    coupon_stats = coupon_stats.merge(c_reqs, on="coupon_id", how="left").fillna(0)
    coupon_stats = coupon_stats.merge(c_usage, on="coupon_id", how="left").fillna(0)

    num_cols = ["discount_value", "minimum_purchase", "coupon_value", "view_count", "req_count", "usage_count"]
    corr_matrix = coupon_stats[num_cols].corr().round(3)
    stats["correlation_matrix"] = corr_matrix.to_dict()

    # Plot 15: Correlation Heatmap
    plt.figure(figsize=(9, 7))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".3f", linewidths=0.5)
    plt.title("Cross-Feature Correlation Matrix (Coupon Telemetry)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "15_numerical_correlation_heatmap.png"), dpi=300)
    plt.close()

    # Save computed metrics to json for documentation accuracy
    stats_path = os.path.join(OUTPUT_DIR, "eda_computed_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"\nSaved computed metrics to: {stats_path}")
    print(f"Generated 15 high-resolution figures in: {OUTPUT_DIR}")

    return stats


def main():
    print("=" * 65)
    print("PHASE 5 - EXPLORATORY DATA ANALYSIS")
    print("Smart Coupon Swap System")
    print("=" * 65)
    dfs = load_datasets()
    analyze_and_plot(dfs)
    print("=" * 65)
    print("EDA execution completed successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()

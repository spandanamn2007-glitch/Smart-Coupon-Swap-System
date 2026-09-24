# Phase 4 — Data Cleaning & Preprocessing Report

> **Smart Coupon Swap System — Phase 4: Data Quality Audit, Standardization & Processing**

---

## 1. Purpose of Phase 4

The purpose of **Phase 4 (Data Cleaning & Preprocessing)** is to perform a rigorous quality inspection, structural verification, format standardization, and referential validation on all synthetic raw datasets generated in Phase 3. 

This phase bridges raw data collection and analytical exploration by creating standard, clean CSV files in `data/processed/` without altering or overwriting the original source files in `data/raw/`.

> **Important Boundary Rule:** In accordance with strict phase-by-phase engineering, Phase 4 is limited to data cleaning and preprocessing. No Exploratory Data Analysis (EDA), correlation matrices, distribution plots, feature engineering, machine learning modeling, or application routes are implemented in this phase.

---

## 2. Pipeline Architecture & Integrity Principles

- **Input Directory:** `data/raw/` (10 raw CSV files — immutable source)
- **Output Directory:** `data/processed/` (10 clean CSV files)
- **Transformation Script:** `scripts/clean_datasets.py`
- **Validation Script:** `scripts/validate_processed_data.py`
- **Immutability Principle:** The raw source files in `data/raw/` were never modified or overwritten during execution.
- **Academic Rigor Principle:** Because Phase 3 generated synthetic datasets using controlled logic and schema validation, data quality issues were evaluated honestly. No artificial data corruption was introduced merely to simulate repairs. Where a dataset was clean as generated, it is reported as **Clean as generated / No remediation required**.

---

## 3. Dataset Audit & Transformation Summary

| Raw Dataset (`data/raw/`) | Processed Dataset (`data/processed/`) | Raw Rows | Clean Rows | Columns | Missing Values (Before $\to$ After) | Duplicate Records (Before $\to$ After) | Records Removed |
|---|---|---|---|---|---|---|---|
| `categories.csv` | `categories_clean.csv` | 10 | 10 | 2 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `brands.csv` | `brands_clean.csv` | 36 | 36 | 3 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `users.csv` | `users_clean.csv` | 500 | 500 | 9 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `coupons.csv` | `coupons_clean.csv` | 2,500 | 2,500 | 14 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `user_preferences.csv` | `user_preferences_clean.csv` | 1,282 | 1,282 | 7 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `coupon_views.csv` | `coupon_views_clean.csv` | 5,000 | 5,000 | 5 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `coupon_requests.csv` | `coupon_requests_clean.csv` | 1,500 | 1,500 | 5 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `coupon_usage.csv` | `coupon_usage_clean.csv` | 1,000 | 1,000 | 5 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| `swaps.csv` | `swaps_clean.csv` | 500 | 500 | 8 | 244 $\to$ 244* | 0 $\to$ 0 | 0 |
| `ratings.csv` | `ratings_clean.csv` | 401 | 401 | 7 | 0 $\to$ 0 | 0 $\to$ 0 | 0 |
| **Total** | | **12,729** | **12,729** | — | **244 $\to$ 244** | **0 $\to$ 0** | **0** |

*\*Note on Missing Values in `swaps.csv`: The 244 null entries in `completed_at` represent uncompleted lifecycle states (`proposed`: 70, `rejected`: 95, `cancelled`: 79). Retaining these nulls is semantically correct; imputing or removing them would corrupt transaction history.*

---

## 4. Detailed Dataset-by-Dataset Audit & Cleaning Actions

### 4.1. `categories.csv` $\to$ `categories_clean.csv`
- **Initial Inspection:** 10 records, 2 columns (`category_id`, `category_name`). No missing values, no duplicates.
- **Cleaning Actions:**
  - Applied string stripping to remove potential whitespace.
  - Verified primary key uniqueness (`category_id`).
  - Standardized explicit string casting.
- **Result:** Clean as generated; 10 records preserved.

### 4.2. `brands.csv` $\to$ `brands_clean.csv`
- **Initial Inspection:** 36 records, 3 columns (`brand_id`, `brand_name`, `category_id`). No missing values, no duplicates.
- **Cleaning Actions:**
  - Applied whitespace trimming on text columns.
  - Validated foreign key reference `category_id` $\to$ `categories.category_id` (100% match).
  - Explicit string type coercion.
- **Result:** Clean as generated; 36 records preserved.

### 4.3. `users.csv` $\to$ `users_clean.csv`
- **Initial Inspection:** 500 records, 9 columns.
- **Cleaning Actions:**
  - Applied whitespace trimming on all categorical and geographic text fields (`gender`, `city`, `state`, `activity_level`).
  - Standardized date formatting: `account_created_date` formatted to ISO `YYYY-MM-DD`.
  - Type casting: `age`, `preferred_discount_min`, and `preferred_discount_max` cast to explicit integers.
  - Logical constraint check: Verified `preferred_discount_min <= preferred_discount_max` across all 500 rows (0 violations).
- **Result:** 500 records verified and formatted.

### 4.4. `coupons.csv` $\to$ `coupons_clean.csv`
- **Initial Inspection:** 2,500 records, 14 columns.
- **Cleaning Actions:**
  - Verified referential integrity: `owner_id` $\in$ `users`, `category_id` $\in$ `categories`, `brand_id` $\in$ `brands` (0 broken keys).
  - Date normalization: `issue_date` and `expiry_date` standardized to `YYYY-MM-DD`.
  - Chronological validation: Verified `expiry_date >= issue_date` across all 2,500 records (0 violations).
  - Range validation: Verified `coupon_value > 0` and `discount_value > 0`. Percentage discounts capped at 100%.
  - Categorical standardization: Normalized `discount_type`, `status`, `source`, and `transferable` to lowercase.
  - Precision standardization: `coupon_value` and `discount_value` rounded to 2 decimal places.
- **Result:** 2,500 records verified and formatted.

### 4.5. `user_preferences.csv` $\to$ `user_preferences_clean.csv`
- **Initial Inspection:** 1,282 records, 7 columns.
- **Cleaning Actions:**
  - Verified foreign keys against `users`, `categories`, and `brands` (100% valid).
  - Normalized `preferred_discount_type` to lowercase.
  - Cast `minimum_discount` to integer.
  - Trimmed string columns.
- **Result:** 1,282 records preserved.

### 4.6. `coupon_views.csv` $\to$ `coupon_views_clean.csv`
- **Initial Inspection:** 5,000 records, 5 columns.
- **Cleaning Actions:**
  - Verified foreign keys `user_id` $\in$ `users` and `coupon_id` $\in$ `coupons`.
  - Formatted `viewed_at` timestamp to ISO standard `YYYY-MM-DD HH:MM:SS`.
  - Cast `view_duration_seconds` to integer; confirmed all values non-negative (range: 5–300s).
- **Result:** 5,000 records preserved.

### 4.7. `coupon_requests.csv` $\to$ `coupon_requests_clean.csv`
- **Initial Inspection:** 1,500 records, 5 columns.
- **Cleaning Actions:**
  - Foreign key verification: `user_id` and `coupon_id` validated against parent tables.
  - Timestamp formatting: `requested_at` normalized to `YYYY-MM-DD HH:MM:SS`.
  - Categorical normalization: Standardized `request_status` (`pending`, `accepted`, `rejected`, `cancelled`) to lowercase.
- **Result:** 1,500 records preserved.

### 4.8. `coupon_usage.csv` $\to$ `coupon_usage_clean.csv`
- **Initial Inspection:** 1,000 records, 5 columns.
- **Cleaning Actions:**
  - Foreign key verification: `user_id` and `coupon_id` validated.
  - Timestamp formatting: `used_at` normalized to `YYYY-MM-DD HH:MM:SS`.
  - Categorical normalization: Standardized `usage_status` (`used`, `expired`, `cancelled`) to lowercase.
- **Result:** 1,000 records preserved.

### 4.9. `swaps.csv` $\to$ `swaps_clean.csv`
- **Initial Inspection:** 500 records, 8 columns.
- **Missing Value Handling:**
  - Exactly 244 records have empty `completed_at` timestamps.
  - Investigation revealed this occurs strictly for `proposed` (70), `rejected` (95), and `cancelled` (79) swaps.
  - For `accepted` (74) and `completed` (182) swaps, `completed_at` is 100% populated.
  - **Decision:** Retained missing values as legitimate representations of uncompleted transactions.
- **Logical Validation:**
  - Confirmed `proposer_id != receiver_id` (no self-swaps: 0 violations).
  - Confirmed `offered_coupon_id != requested_coupon_id` (0 violations).
  - Verified `completed_at >= proposed_at` for all completed swaps.
- **Formatting:** `proposed_at` and `completed_at` formatted to ISO standard timestamps.
- **Result:** 500 records preserved.

### 4.10. `ratings.csv` $\to$ `ratings_clean.csv`
- **Initial Inspection:** 401 records, 7 columns.
- **Cleaning Actions:**
  - Verified foreign keys: `swap_id` $\in$ `swaps`, `rater_id` $\in$ `users`, `rated_user_id` $\in$ `users`.
  - Confirmed `rater_id != rated_user_id` (no self-ratings: 0 violations).
  - Validated rating range: Integer scale strictly within [1, 5].
  - Normalized `rated_at` timestamp format.
  - Trimmed review feedback text strings.
- **Result:** 401 records preserved.

---

## 5. Cross-Dataset Relationship Verification

All foreign-key paths were re-evaluated across the processed datasets:

- `brands_clean.category_id` $\to$ `categories_clean.category_id`: **Valid**
- `coupons_clean.owner_id` $\to$ `users_clean.user_id`: **Valid**
- `coupons_clean.category_id` $\to$ `categories_clean.category_id`: **Valid**
- `coupons_clean.brand_id` $\to$ `brands_clean.brand_id`: **Valid**
- `user_preferences_clean.user_id` $\to$ `users_clean.user_id`: **Valid**
- `coupon_views_clean.user_id` $\to$ `users_clean.user_id`: **Valid**
- `coupon_views_clean.coupon_id` $\to$ `coupons_clean.coupon_id`: **Valid**
- `coupon_requests_clean.user_id` $\to$ `users_clean.user_id`: **Valid**
- `coupon_requests_clean.coupon_id` $\to$ `coupons_clean.coupon_id`: **Valid**
- `coupon_usage_clean.user_id` $\to$ `users_clean.user_id`: **Valid**
- `coupon_usage_clean.coupon_id` $\to$ `coupons_clean.coupon_id`: **Valid**
- `swaps_clean.proposer_id` $\to$ `users_clean.user_id`: **Valid**
- `swaps_clean.receiver_id` $\to$ `users_clean.user_id`: **Valid**
- `swaps_clean.offered_coupon_id` $\to$ `coupons_clean.coupon_id`: **Valid**
- `swaps_clean.requested_coupon_id` $\to$ `coupons_clean.coupon_id`: **Valid**
- `ratings_clean.swap_id` $\to$ `swaps_clean.swap_id`: **Valid**
- `ratings_clean.rater_id` $\to$ `users_clean.user_id`: **Valid**
- `ratings_clean.rated_user_id` $\to$ `users_clean.user_id`: **Valid**

---

## 6. Verification Results

Running `python scripts/validate_processed_data.py`:
```
=================================================================
PHASE 4 - PROCESSED DATASET INTEGRITY VALIDATION
=================================================================
[PASS] All 10 required processed CSV files exist
[PASS] All 10 raw CSV files still exist in data/raw/
[PASS] Required columns present in all processed datasets
[PASS] Primary IDs are strictly unique in processed datasets
[PASS] No unintended missing values in required columns
[PASS] swaps.completed_at null only when swap is uncompleted
[PASS] Foreign-key relationships strictly valid across all processed tables
[PASS] Numeric fields within strictly valid ranges
[PASS] Coupon dates valid (expiry_date >= issue_date)
[PASS] No self-ratings in processed ratings (rater_id != rated_user_id)
[PASS] Swaps logical integrity (proposer != receiver, offered != requested)
[PASS] Raw datasets preserved and row counts match processed datasets
=================================================================
RESULTS: 12/12 validation checks passed.
=================================================================
```

---

## 7. Limitations of Preprocessed Data

1. **Synthetic Nature:** Preprocessing cleans and structures synthetic data generated under parametric distributions. The datasets do not capture messy real-world artifacts such as missing user survey data or corrupted web crawler text.
2. **Absence of Engineered Features:** In strict adherence to phase boundaries, this phase avoided creating derived ML features (e.g., user tenure, coupon remaining validity ratio, brand popularity score). These belong in **Phase 6 (Feature Engineering)**.
3. **No Target Encoding / Scaling:** Numerical features have not been normalized (MinMax or StandardScaler) and categorical features have not been one-hot or target encoded. Scaling and encoding will be carried out alongside model training pipelines.

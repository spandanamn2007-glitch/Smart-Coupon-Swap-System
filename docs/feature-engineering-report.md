# Phase 6 — Feature Engineering Specification & Report

> **Smart Coupon Swap System — Phase 6: Feature Extraction & Representation Engineering**

---

## 1. Objective

The goal of **Part A of Phase 6** is to engineer informative, structured, domain-aligned feature representations from the preprocessed relational datasets (`data/processed/*.csv`).

These feature sets prepare the codebase for upcoming machine learning, recommendation, swap matching, demand forecasting, and anomaly detection models without mutating the clean source data or violating phase boundaries.

> **Data Leakage & Integrity Boundary:** No target variables (such as future swap acceptance state or post-swap ratings) are used to predict themselves. All feature aggregations are computed exclusively from non-conflicting historical dimensions.

---

## 2. Input Datasets & Feature Datasets

### Source Datasets (`data/processed/`):
- `users_clean.csv`, `coupons_clean.csv`, `categories_clean.csv`, `brands_clean.csv`, `user_preferences_clean.csv`, `coupon_views_clean.csv`, `coupon_requests_clean.csv`, `coupon_usage_clean.csv`, `swaps_clean.csv`, `ratings_clean.csv`

### Engineered Output Feature Datasets (`data/features/`):
| Feature Dataset | Key Entity | Row Count | Feature Columns | Description |
|---|---|---|---|---|
| `user_features.csv` | `user_id` | 500 | 21 | User demographic, preference range, behavioral volume, reputation, and activity features. |
| `coupon_features.csv` | `coupon_id` | 2,500 | 23 | Value ratios, effective discount percentages, validity duration, and engagement conversion rates. |
| `interaction_features.csv` | (`user_id`, `coupon_id`) | 7,476 | 7 | Cross-user/coupon interaction intensity, dwell time, request/usage counts, and weighted interaction scores. |
| `swap_pair_features.csv` | `swap_id` | 500 | 13 | Bilateral swap parity metrics, value ratios, category/brand matching flags, and resolution latency. |

---

## 3. Feature Definitions & Group Specifications

### 3.1. User Features (`data/features/user_features.csv`)
- `user_id` (String): Unique user identifier.
- `age` (Int): User age.
- `gender` (String): User gender classification.
- `city`, `state` (String): Geographic residence.
- `preferred_discount_min`, `preferred_discount_max` (Int): User discount preference bounds.
- `preferred_discount_range` (Int): Feature derived as `preferred_discount_max - preferred_discount_min`.
- `total_views_count` (Int): Total coupons viewed by user.
- `avg_view_duration` (Float): Average dwell time across all views by user.
- `total_requests_count` (Int): Unilateral requests submitted.
- `accepted_requests_count` (Int): Requests accepted by listing owners.
- `total_usage_count` (Int): Redemption count.
- `swaps_proposed_count` (Int): Swaps initiated by user.
- `swaps_received_count` (Int): Swaps targeted at user.
- `swaps_completed_count` (Int): Total completed swaps involving user.
- `avg_rating_received` (Float): Mean score received from counterparties.
- `ratings_count` (Int): Number of ratings received.
- `total_preferences_count` (Int): Explicit preferences set.

### 3.2. Coupon Features (`data/features/coupon_features.csv`)
- `coupon_id` (String): Primary Key.
- `coupon_value` (Float): Face value in currency units.
- `discount_value` (Float): Discount magnitude.
- `minimum_purchase` (Int): Qualifying minimum spend threshold.
- `effective_discount_pct` (Float): Percentage discount equivalent calculated as `(discount_value / coupon_value) * 100` for flat discounts or native percentage value.
- `validity_duration_days` (Int): Period elapsed from `issue_date` to `expiry_date`.
- `total_views_count` (Int): Total views received.
- `avg_view_duration` (Float): Average view duration per coupon.
- `total_requests_count` (Int): Total requests received.
- `request_conversion_rate` (Float): Derived conversion metric `total_requests_count / total_views_count`.
- `total_usage_count` (Int): Total usage events.
- `swap_offered_count`, `swap_requested_count` (Int): Appearances in swap proposals.

### 3.3. Interaction Features (`data/features/interaction_features.csv`)
- `user_id`, `coupon_id` (Strings): Composite entity pair key.
- `view_count` (Int): Views by user for coupon.
- `total_view_duration` (Int): Cumulative dwell time.
- `request_count` (Int): Requests submitted by user for coupon.
- `usage_count` (Int): Usage events by user for coupon.
- `interaction_score` (Int): Weighted composite affinity score computed as:
  $$\text{Score} = (1 \times \text{view\_count}) + (3 \times \text{request\_count}) + (5 \times \text{usage\_count})$$

### 3.4. Swap Pair Features (`data/features/swap_pair_features.csv`)
- `swap_id` (String): Primary Key.
- `value_difference` (Float): Absolute difference in face values `|offered_value - requested_value|`.
- `value_ratio` (Float): Ratio of offered to requested values `offered_value / requested_value`.
- `category_match` (Int): Binary indicator (1 if offered and requested coupons share category_id, else 0).
- `brand_match` (Int): Binary indicator (1 if offered and requested coupons share brand_id, else 0).
- `proposer_avg_rating`, `receiver_avg_rating` (Float): Historical reputation scores of counterparties.
- `swap_turnaround_hours` (Float): Hours elapsed between proposal and completed settlement.

---

## 4. Leakage Prevention & Imputation Strategy

1. **No Target Leakage:** Features calculated for user behavior or swap pairs do not include post-event settlement indicators as input features for training datasets.
2. **Missing Value Handling:** Missing interaction counts are imputed with `0`, missing dwell times with `0.0`, and unrated users default to a neutral rating score of `3.0`.
3. **Data Preservation:** Processed files in `data/processed/` and raw files in `data/raw/` remain 100% untouched.

# Phase 5 — Exploratory Data Analysis (EDA) Report

> **Smart Coupon Swap System — Phase 5: Comprehensive Statistical & Behavioral Exploration**

---

## 1. Objective of Phase 5

The objective of **Phase 5 (Exploratory Data Analysis)** is to conduct an in-depth, rigorous empirical exploration of the cleaned and preprocessed datasets generated in Phase 4 (`data/processed/*.csv`). 

This analysis investigates:
- Statistical distributions and dispersion metrics of demographic, transactional, and preference features
- Behavioral telemetry patterns across the user engagement funnel (views $\to$ requests $\to$ usage)
- Bilateral swap dynamics, proposal resolution rates, and settlement turnaround times
- Counterparty reputation feedback patterns
- Inter-feature correlations and outlier checks across key entities

> **Strict Phase Boundary Notice:** This analysis is strictly descriptive. No feature engineering, data transformations, machine learning algorithms, recommendation systems, or predictive models have been implemented. Correlation does not imply causation. All findings are derived directly from the computed values of the processed datasets.

---

## 2. Processed Datasets Analyzed

All 10 processed CSV datasets located in `data/processed/` were ingested and analyzed:

| # | Dataset File | Rows | Columns | Entity Type | Primary Key |
|---|---|---|---|---|---|
| 1 | `categories_clean.csv` | 10 | 2 | Vertical Taxonomy | `category_id` |
| 2 | `brands_clean.csv` | 36 | 3 | Merchant Brands | `brand_id` |
| 3 | `users_clean.csv` | 500 | 9 | User Accounts | `user_id` |
| 4 | `coupons_clean.csv` | 2,500 | 14 | Coupon Listings | `coupon_id` |
| 5 | `user_preferences_clean.csv` | 1,282 | 7 | Category/Brand Affinities | `preference_id` |
| 6 | `coupon_views_clean.csv` | 5,000 | 5 | Browsing Telemetry | `view_id` |
| 7 | `coupon_requests_clean.csv` | 1,500 | 5 | Acquisition Requests | `request_id` |
| 8 | `coupon_usage_clean.csv` | 1,000 | 5 | Redemption Lifecycle | `usage_id` |
| 9 | `swaps_clean.csv` | 500 | 8 | Bilateral Swap Proposals | `swap_id` |
| 10 | `ratings_clean.csv` | 401 | 7 | Counterparty Reviews | `rating_id` |

**Total Analyzed Records:** 12,729 rows.

---

## 3. Data Quality & Pre-Analysis Verification

- **Completeness:** 100% complete across all required primary and secondary fields. The only missing values occur in `swaps_clean.csv` (`completed_at`, 244 records), which represent uncompleted transactions (`proposed`: 70, `rejected`: 95, `cancelled`: 79) and are structurally expected.
- **Uniqueness:** 0 duplicate primary IDs; 0 duplicate records.
- **Referential Integrity:** 100% valid cross-table foreign key relationships with zero orphan records.
- **Value Consistency:** All numeric and date constraints (`expiry_date >= issue_date`, `completed_at >= proposed_at`, `coupon_value > 0`, `rating` $\in [1, 5]$) strictly validated.

---

## 4. Key Descriptive Statistics (Actual Computed Metrics)

### 4.1. User Demographics (`users_clean.csv`)
- **Total Users:** 500
- **Age Distribution:**
  - Mean: **42.91 years** | Std Dev: **13.16 years**
  - Min: **18 years** | Median (50%): **44.00 years** | Max: **65 years**
  - 25th Percentile: **32.00 years** | 75th Percentile: **54.00 years**
  - Interquartile Range (IQR): **22.00 years** | Outliers Detected: **0**
- **Gender Breakdown:**
  - Male: **243** (48.6%)
  - Female: **236** (47.2%)
  - Other: **21** (4.2%)
- **Activity Level Distribution:**
  - Medium: **252** (50.4%)
  - Low: **128** (25.6%)
  - High: **120** (24.0%)
- **User Preferred Minimum Discount:**
  - Mean: **22.54%** | Min: **5%** | Median: **23%** | Max: **40%**
- **User Preferred Maximum Discount:**
  - Mean: **51.96%** | Min: **18%** | Median: **52%** | Max: **90%**

### 4.2. Coupon Assets (`coupons_clean.csv`)
- **Total Coupons:** 2,500
- **Coupon Value (Currency Units):**
  - Mean: **2,575.07** | Std Dev: **1,420.33**
  - Min: **50.97** | Median: **2,585.78** | Max: **4,998.81**
  - 25th Percentile: **1,378.98** | 75th Percentile: **3,784.14** | Outliers Detected: **0**
- **Discount Value:**
  - Mean: **106.66** | Std Dev: **125.13**
  - Min: **5.00** | Median: **57.30** | Max: **500.00** (reflecting combination of percentage discounts 5–80% and flat discounts 50–500)
- **Minimum Qualifying Purchase:**
  - Mean: **790.21** | Std Dev: **686.08** | Median: **499.00** | Max: **1,999.00**
- **Coupon Validity Duration:**
  - Mean: **198.42 days** | Min: **30 days** | Median: **200 days** | Max: **365 days**

### 4.3. Behavioral Engagement Funnel
- **Browsing Telemetry (`coupon_views`):** 5,000 views
  - View Dwell Time: Mean **153.70s** | Median **154.50s** | Range **5s – 300s**
- **Acquisition Requests (`coupon_requests`):** 1,500 requests
  - Status Breakdown: `pending`: **451** (30.1%), `accepted`: **429** (28.6%), `rejected`: **393** (26.2%), `cancelled`: **227** (15.1%)
- **Redemption / Usage Lifecycle (`coupon_usage`):** 1,000 events
  - Status Breakdown: `used`: **607** (60.7%), `expired`: **257** (25.7%), `cancelled`: **136** (13.6%)

### 4.4. Swap Dynamics (`swaps_clean.csv`)
- **Total Swap Proposals:** 500
- **Proposal Resolution Breakdown:**
  - `completed`: **182** (36.4%)
  - `rejected`: **95** (19.0%)
  - `cancelled`: **79** (15.8%)
  - `accepted`: **74** (14.8%)
  - `proposed` (pending): **70** (14.0%)
- **Turnaround Settlement Time (for resolved swaps):**
  - Sample Size: **256 swaps** (`completed` + `accepted`)
  - Mean Turnaround: **37.20 hours** | Std Dev: **20.88 hours**
  - Min Turnaround: **1.00 hour** | Median: **37.00 hours** | Max Turnaround: **72.00 hours**

### 4.5. Counterparty Reputation Ratings (`ratings_clean.csv`)
- **Total Ratings:** 401
- **Score Distribution (1 to 5 Stars):**
  - Mean Rating: **3.00** | Std Dev: **1.41**
  - Score 1: **83** (20.7%)
  - Score 2: **72** (18.0%)
  - Score 3: **83** (20.7%)
  - Score 4: **86** (21.4%)
  - Score 5: **77** (19.2%)

---

## 5. Cross-Dataset Correlation Matrix

A temporary merged view evaluated linear dependencies between coupon features and behavioral telemetry (view count, request count, usage count):

| Metric | `discount_value` | `minimum_purchase` | `coupon_value` | `view_count` | `req_count` | `usage_count` |
|---|---|---|---|---|---|---|
| `discount_value` | **1.000** | -0.017 | 0.017 | 0.013 | -0.012 | 0.002 |
| `minimum_purchase` | -0.017 | **1.000** | 0.022 | -0.001 | 0.012 | 0.015 |
| `coupon_value` | 0.017 | 0.022 | **1.000** | 0.010 | -0.034 | -0.001 |
| `view_count` | 0.013 | -0.001 | 0.010 | **1.000** | -0.011 | 0.026 |
| `req_count` | -0.012 | 0.012 | -0.034 | -0.011 | **1.000** | 0.011 |
| `usage_count` | 0.002 | 0.015 | -0.001 | 0.026 | 0.011 | **1.000** |

### Interpretation:
- Correlations between monetary parameters (`coupon_value`, `discount_value`, `minimum_purchase`) and engagement metrics (`view_count`, `req_count`, `usage_count`) are near zero ($|r| < 0.04$).
- This empirical result confirms that interaction events are distributed uniformly across items, which is standard for synthetic baseline data before feature engineering constructs non-linear interaction terms in Phase 6.

---

## 6. Generated Visualizations Reference (`outputs/eda/`)

All 15 figures were generated at 300 DPI and saved in [`outputs/eda/`](file:///C:/Users/chand/.gemini/antigravity/scratch/smart-coupon-swap-system/outputs/eda):

1. **`01_category_coupon_distribution.png`**: Bar plot showing coupon distribution across all 10 categories (range: 230 in Grocery to 276 in Electronics).
2. **`02_brands_per_category.png`**: Brand allocation per category (3–4 brands per category).
3. **`03_user_age_distribution.png`**: Histogram with KDE and boxplot demonstrating normal user age distribution (18–65 years).
4. **`04_user_geographic_distribution.png`**: User geographical spread across 20 metropolitan cities.
5. **`05_user_activity_and_gender.png`**: Activity levels (low, medium, high) segmented by gender.
6. **`06_coupon_value_distribution.png`**: Boxplot and histogram displaying uniform value spread from 50 to 5,000 units.
7. **`07_coupon_type_and_status.png`**: Count plots contrasting discount types (percentage vs flat) and coupon statuses.
8. **`08_coupon_validity_duration.png`**: Frequency distribution of validity days (mean: 198.42 days).
9. **`09_user_engagement_funnel.png`**: Comparative volume bar chart showing engagement drop-off: 5,000 views $\to$ 1,500 requests $\to$ 1,000 usage events.
10. **`10_view_duration_distribution.png`**: Browsing dwell time histogram (5–300 seconds).
11. **`11_swap_status_distribution.png`**: Swap resolution counts (182 completed, 95 rejected, 79 cancelled, 74 accepted, 70 proposed).
12. **`12_monthly_swap_proposals.png`**: Time series trend of monthly swap proposals across 2023–2025.
13. **`13_swap_turnaround_time.png`**: Settlement latency distribution for accepted/completed swaps (1–72 hours).
14. **`14_rating_distribution.png`**: Distribution of star ratings from 1 to 5.
15. **`15_numerical_correlation_heatmap.png`**: Annotated heatmap displaying inter-feature correlation coefficients.

---

## 7. Key Analytical Findings

1. **Category Balance:** Coupons are evenly distributed across categories, with Electronics (276) having the highest representation and Grocery (230) the lowest.
2. **Demographic Symmetry:** User demographics display balanced gender representation (48.6% Male, 47.2% Female) and uniform geographic dispersion across tier-1 and tier-2 hubs.
3. **Swap Completion Rate:** 36.4% of proposed swaps reach full completion, while 19.0% are rejected and 15.8% cancelled. This provides balanced positive/negative outcome targets for Phase 11 (Acceptance Likelihood Prediction).
4. **Turnaround Efficiency:** Swaps that reach completion do so within an average of 37.20 hours, with a maximum window of 72 hours.
5. **Reputation Baseline:** Ratings are uniformly distributed across the 1–5 scale with an exact mean of 3.00, providing an unbiased baseline for future collaborative filtering and counterparty scoring.

---

## 8. Limitations & Methodological Constraints

1. **Synthetic Linearity:** Because raw data generation relied on parameterized distributions, raw correlations between independent entities are near zero. Non-linear relationships must be synthesized via Feature Engineering in Phase 6.
2. **Descriptive Scope:** All metrics describe observed historical states. No inferences, predictive probabilities, or ranking models are constructed in this phase.
3. **No Causality Implied:** Observed frequencies indicate observational co-occurrence rather than behavioral causality.

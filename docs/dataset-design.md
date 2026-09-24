# Dataset Design & Specification

> **Smart Coupon Swap System — Phase 3: Dataset Generation & Collection**

---

## 1. Purpose of Phase 3

The objective of **Phase 3 (Dataset Generation / Collection)** is to construct a comprehensive, internally consistent, domain-aligned set of relational datasets in raw CSV format. These datasets represent realistic entities, behavioral telemetry, and transactional histories within a peer-to-peer coupon exchange ecosystem.

All data generated in this phase serves as the empirical foundation for upcoming project phases:
- **Phase 4:** Data Cleaning & Preprocessing
- **Phase 5:** Exploratory Data Analysis (EDA)
- **Phase 6:** Feature Engineering
- **Phases 10–14:** Machine Learning modeling (Recommendation, Acceptance Prediction, Swap Compatibility, Multi-User Graph Matching, Demand Forecasting, Anomaly Detection)

> **Important Boundary Rule:** No machine learning model is trained, evaluated, or benchmarked in Phase 3. No preprocessing, imputation, or feature transformations have been applied to raw files. All datasets are strictly synthetic.

---

## 2. Generation Methodology & Reproducibility

- **Generation Script:** `scripts/generate_datasets.py`
- **Validation Script:** `scripts/validate_datasets.py`
- **Output Directory:** `data/raw/`
- **Random Seed:** `SEED = 42` (ensures 100% deterministic, reproducible generation across platforms)
- **Privacy & Safety:** All user profiles, transaction logs, and brand affiliations are strictly synthetic. No real personally identifiable information (PII), proprietary vendor data, or live voucher codes are present.
- **Relational Integrity:** Foreign keys and cross-table constraints are strictly enforced at generation time to prevent orphan keys, invalid date intervals, and self-referential paradoxes.

---

## 3. Dataset Summary Matrix

| Dataset File | Entity / Domain | Primary Key | Foreign Keys | Row Count |
|---|---|---|---|---|
| `categories.csv` | Coupon Categories | `category_id` | None | 10 |
| `brands.csv` | Merchant Brands | `brand_id` | `category_id` | 36 |
| `users.csv` | User Demographics & Profiles | `user_id` | None | 500 |
| `coupons.csv` | Coupon Listings | `coupon_id` | `owner_id`, `category_id`, `brand_id` | 2,500 |
| `user_preferences.csv` | User Affinity & Preferences | `preference_id` | `user_id`, `preferred_category_id`, `preferred_brand_id` | 1,282 |
| `coupon_views.csv` | Browsing & Engagement Telemetry | `view_id` | `user_id`, `coupon_id` | 5,000 |
| `coupon_requests.csv` | Acquisition Intent & Direct Requests | `request_id` | `user_id`, `coupon_id` | 1,500 |
| `coupon_usage.csv` | Redemption & Expiry Lifecycle | `usage_id` | `user_id`, `coupon_id` | 1,000 |
| `swaps.csv` | Bilateral Swap Proposals & History | `swap_id` | `proposer_id`, `receiver_id`, `offered_coupon_id`, `requested_coupon_id` | 500 |
| `ratings.csv` | Counterparty Ratings & Reviews | `rating_id` | `swap_id`, `rater_id`, `rated_user_id` | 401 |

**Total Synthetic Records:** 12,729 across 10 CSV datasets.

---

## 4. Detailed Dataset Schemas

### 4.1. `categories.csv`
- **File Location:** `data/raw/categories.csv`
- **Description:** Broad marketplace verticals classifying coupons and brand offerings.
- **Attributes:**
  - `category_id` (String): Unique identifier (`CAT01`–`CAT10`).
  - `category_name` (String): Vertical taxonomy (`Food`, `Fashion`, `Electronics`, `Travel`, `Grocery`, `Beauty`, `Entertainment`, `Sports`, `Health`, `Home`).

### 4.2. `brands.csv`
- **File Location:** `data/raw/brands.csv`
- **Description:** Commercial retail, merchant, or e-commerce brands offering promotional vouchers.
- **Attributes:**
  - `brand_id` (String): Unique identifier (`B001`–`B036`).
  - `brand_name` (String): Synthetic brand name (e.g., `QuickBite`, `TechNova`, `StreamFlix`).
  - `category_id` (String): Reference to parent category in `categories.csv`.

### 4.3. `users.csv`
- **File Location:** `data/raw/users.csv`
- **Description:** Synthetic account holders who list, view, request, and exchange vouchers.
- **Attributes:**
  - `user_id` (String): Unique identifier (`U0001`–`U0500`).
  - `age` (Integer): User age between 18 and 65 years.
  - `gender` (String): Controlled set: `Male` (48%), `Female` (48%), `Other` (4%).
  - `city` (String): Geographic residence across 20 representative tier-1/tier-2 metropolitan areas.
  - `state` (String): Corresponding administrative state.
  - `account_created_date` (Date, `YYYY-MM-DD`): Registration date between 2022-01-01 and 2024-12-31.
  - `preferred_discount_min` (Integer): Minimum acceptable discount value/percentage.
  - `preferred_discount_max` (Integer): Maximum expected discount value/percentage.
  - `activity_level` (String): User activity classification (`low`, `medium`, `high`).

### 4.4. `coupons.csv`
- **File Location:** `data/raw/coupons.csv`
- **Description:** Core coupon assets uploaded or held by users on the exchange.
- **Attributes:**
  - `coupon_id` (String): Unique identifier (`CP0001`–`CP2500`).
  - `owner_id` (String): FK referencing `users.user_id`.
  - `category_id` (String): FK referencing `categories.category_id`.
  - `brand_id` (String): FK referencing `brands.brand_id`.
  - `discount_type` (String): Controlled set: `percentage` (65%), `flat` (35%).
  - `discount_value` (Float): Numerical discount magnitude (5.0–80.0% for percentage; 50–500 currency units for flat).
  - `minimum_purchase` (Integer): Minimum qualifying cart spend (0, 199, 299, 499, 999, 1499, 1999).
  - `issue_date` (Date, `YYYY-MM-DD`): Date voucher became effective.
  - `expiry_date` (Date, `YYYY-MM-DD`): Date voucher expires (strictly `>= issue_date`).
  - `coupon_value` (Float): Estimated face value in standard currency units (50.00–5000.00).
  - `status` (String): Controlled set: `available`, `claimed`, `expired`, `swapped`.
  - `city` (String): Geographic relevance / validity location.
  - `source` (String): Acquisition origin (`purchased`, `gifted`, `earned`, `referral`).
  - `transferable` (String): Policy flag (`yes`, `no`).

### 4.5. `user_preferences.csv`
- **File Location:** `data/raw/user_preferences.csv`
- **Description:** Explicit user affinity records mapping interests in specific categories and brands.
- **Attributes:**
  - `preference_id` (String): Unique identifier (`PR0001`–`PR1282`).
  - `user_id` (String): FK referencing `users.user_id` (1 to 4 preferences per user).
  - `preferred_category_id` (String): FK referencing `categories.category_id`.
  - `preferred_brand_id` (String): FK referencing `brands.brand_id`.
  - `minimum_discount` (Integer): Threshold minimum discount expected for this vertical.
  - `preferred_city` (String): Target location preference.
  - `preferred_discount_type` (String): Preferred mechanism: `percentage`, `flat`, or `any`.

### 4.6. `coupon_views.csv`
- **File Location:** `data/raw/coupon_views.csv`
- **Description:** High-frequency clickstream and browsing telemetry records.
- **Attributes:**
  - `view_id` (String): Unique identifier (`V00001`–`V05000`).
  - `user_id` (String): FK referencing `users.user_id`.
  - `coupon_id` (String): FK referencing `coupons.coupon_id`.
  - `viewed_at` (Timestamp, `YYYY-MM-DD HH:MM:SS`): Event timestamp.
  - `view_duration_seconds` (Integer): Engagement dwell time in seconds (5–300 seconds).

### 4.7. `coupon_requests.csv`
- **File Location:** `data/raw/coupon_requests.csv`
- **Description:** Explicit unilateral user expressions of interest to claim or request a coupon.
- **Attributes:**
  - `request_id` (String): Unique identifier (`REQ0001`–`REQ1500`).
  - `user_id` (String): Requesting user FK referencing `users.user_id`.
  - `coupon_id` (String): Requested coupon FK referencing `coupons.coupon_id`.
  - `requested_at` (Timestamp, `YYYY-MM-DD HH:MM:SS`): Request submission timestamp.
  - `request_status` (String): Controlled state: `pending`, `accepted`, `rejected`, `cancelled`.

### 4.8. `coupon_usage.csv`
- **File Location:** `data/raw/coupon_usage.csv`
- **Description:** Lifecycle closure events recording final redemption, cancellation, or expiration.
- **Attributes:**
  - `usage_id` (String): Unique identifier (`USE0001`–`USE1000`).
  - `user_id` (String): Redeeming user FK referencing `users.user_id`.
  - `coupon_id` (String): Redeemed coupon FK referencing `coupons.coupon_id`.
  - `used_at` (Timestamp, `YYYY-MM-DD HH:MM:SS`): Event execution timestamp.
  - `usage_status` (String): Outcome status: `used`, `expired`, `cancelled`.

### 4.9. `swaps.csv`
- **File Location:** `data/raw/swaps.csv`
- **Description:** Bilateral exchange transactions proposed between two distinct users exchanging coupons.
- **Attributes:**
  - `swap_id` (String): Unique identifier (`SW0001`–`SW0500`).
  - `proposer_id` (String): Initiating user FK referencing `users.user_id`.
  - `receiver_id` (String): Target counterparty FK referencing `users.user_id` (`proposer_id != receiver_id`).
  - `offered_coupon_id` (String): Offered coupon FK referencing `coupons.coupon_id`.
  - `requested_coupon_id` (String): Requested coupon FK referencing `coupons.coupon_id` (`offered != requested`).
  - `proposed_at` (Timestamp, `YYYY-MM-DD HH:MM:SS`): Proposal timestamp.
  - `completed_at` (Timestamp or empty): Settlement timestamp (populated for `accepted` and `completed`).
  - `swap_status` (String): State machine: `proposed`, `accepted`, `rejected`, `completed`, `cancelled`.

### 4.10. `ratings.csv`
- **File Location:** `data/raw/ratings.csv`
- **Description:** Post-swap counterparty trust and reputation feedback.
- **Attributes:**
  - `rating_id` (String): Unique identifier (`RAT0001`–`RAT0401`).
  - `swap_id` (String): FK referencing `swaps.swap_id` (limited to accepted/completed swaps).
  - `rater_id` (String): Rating user FK referencing `users.user_id`.
  - `rated_user_id` (String): Rated counterparty FK referencing `users.user_id` (`rater_id != rated_user_id`).
  - `rating` (Integer): Discrete score between 1 and 5.
  - `review_text` (String): Synthetic feedback comment.
  - `rated_at` (Timestamp, `YYYY-MM-DD HH:MM:SS`): Feedback submission timestamp.

---

## 5. Cross-Dataset Relational Architecture

The datasets maintain exact foreign key dependencies reflecting the real platform relational model:

```
[categories] ──1:N──< [brands]
     │                   │
     │ 1:N               │ 1:N
     v                   v
 [user_preferences]  [coupons] ──1:N──< [coupon_views]
        ^                │
        │                ├──1:N──< [coupon_requests]
        │                │
        │ 1:N            ├──1:N──< [coupon_usage]
        │                │
     [users] ────────────┼──1:N──< [swaps] ──1:N──< [ratings]
                         │           │
                         └───────────┘ (offered & requested)
```

---

## 6. Alignment with Future Machine Learning & Data Science Phases

| Planned ML Component | Target Phase | Primary Datasets Utilized | Role of Raw Data |
|---|---|---|---|
| **Coupon Recommendation** | Phase 10 | `user_preferences`, `coupon_views`, `coupons`, `categories`, `brands` | Feature inputs for collaborative filtering, implicit matrix factorization, and content-based cosine similarity. |
| **Acceptance Likelihood Prediction** | Phase 11 | `swaps`, `users`, `coupons`, `user_preferences` | Training labels (`swap_status` accepted vs rejected) and feature vectors representing user discount alignment and value symmetry. |
| **Bilateral Swap Compatibility** | Phase 12 | `coupons`, `user_preferences`, `swaps` | Scoring parity between offered and requested coupon parameters (value, expiry, brand affinity). |
| **Multi-User Swap Cycles** | Phase 13 | `coupons`, `swaps`, `user_preferences` | Edge definition for directed exchange multigraphs ($A \to B \to C \to A$) to discover multi-party coincidence of wants. |
| **Demand Forecasting** | Phase 14 | `coupons`, `coupon_views`, `coupon_requests`, `coupon_usage` | Aggregated demand tiers (High/Medium/Low) based on view-to-request conversion ratios and interaction volume. |
| **Anomaly & Fraud Detection** | Phase 14 | `users`, `coupons`, `coupon_views`, `swaps`, `ratings` | Outlier detection baselines for suspicious upload frequency, extreme discount skew, or rating anomalies. |

---

## 7. Limitations of Synthetic Data

1. **Synthetic Behavioral Patterns:** Clickstream intervals, dwell times, and request frequencies reflect parameterized random distributions rather than complex human cognitive browsing behavior.
2. **Simplified Textual Semantics:** Review comments and brand labels are drawn from fixed synthetic lexicons and do not exhibit authentic natural-language nuances, colloquialisms, or typographical errors.
3. **Absence of Real Market Volatility:** Seasonal shopping spikes (e.g., holiday sales, festival periods) are modeled uniformly across dates rather than mirroring real macroeconomic cycles.
4. **Scope Integrity:** The raw datasets are purposefully stored without cleaning or normalization to allow Phase 4 (Data Cleaning & Preprocessing) to realistically demonstrate standard data hygiene practices.

# Phase 7 — Core Platform Features & Data Science Integration Report

## Executive Summary
Phase 7 implements the core business logic, recommendation engine, graph-based circular swap matching, machine learning prediction models, anomaly detection, demand forecasting, and notification systems for the **Smart Coupon Swap System**. All components interface cleanly with the MySQL database and Flask REST API foundation established in Phase 6.

---

## Architecture Overview

```
                          ┌───────────────────────────┐
                          │   Flask REST API Layer    │
                          └─────────────┬─────────────┘
                                        │
      ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
      │                  │              │              │                  │
┌─────▼──────┐    ┌──────▼─────┐  ┌─────▼──────┐ ┌─────▼──────┐    ┌─────▼──────┐
│Marketplace │    │Recommend-  │  │  2-Way &   │ │ Machine    │    │  System    │
│ & Search   │    │  ations    │  │ 3-Way Swap │ │  Learning  │    │Notifica-   │
│ Service    │    │  Service   │  │   Engine   │ │ Models     │    │   tions    │
└─────┬──────┘    └──────┬─────┘  └─────┬──────┘ └─────┬──────┘    └─────┬──────┘
      │                  │              │              │                  │
      └──────────────────┴──────────────┼──────────────┴──────────────────┘
                                        │
                          ┌─────────────▼─────────────┐
                          │   MySQL 8.x Database &    │
                          │   Pre-trained ML Models   │
                          └───────────────────────────┘
```

---

## Implemented Components & Feature Matrix

### Part A — Coupon Marketplace & Search/Filtering
- **Endpoints:** `GET /api/coupons`, `GET /api/coupons/<id>`, `POST /api/coupons`, `PUT /api/coupons/<id>`, `DELETE /api/coupons/<id>`
- **Dynamic Parameterized Search:** Filters by `category_id`, `brand_id`, `discount_type`, `min_discount`, `keyword` (title/description/category/brand match), and sorting (`created_desc`, `discount_desc`, `expiry_asc`).
- **Security & Authorization:** `@login_required` boundary checks on creation, update, and deletion ensuring users can only mutate coupons they own (`owner_id == session["user_id"]`).

### Part B — Explainable Recommendation System
- **Endpoint:** `GET /api/recommendations`
- **Algorithm:** Scoring formula combining:
  1. Category Preference Alignment (35%)
  2. Brand Preference Alignment (25%)
  3. Minimum Preferred Discount Threshold Met (20%)
  4. Seller Reputation Score (20%)
- **Explainability:** Each returned coupon includes a natural language `explanation` detailing why it was recommended (e.g., *"Matches preferred category Food & Dining and merchant Swiggy"*).

### Part C — Swap Acceptance Prediction Model
- **Endpoint:** `POST /api/predictions/acceptance`
- **Artifact:** `models/acceptance_model.joblib`
- **Model Type:** `RandomForestClassifier` trained on feature dataset `data/features/swaps_features.csv`.
- **Performance Metrics:**
  - **Accuracy:** 65.12%
  - **Precision:** 69.81%
  - **Recall:** 72.55%
  - **F1 Score:** 71.15%
  - **ROC-AUC:** 67.11%
- **Features Used:** `value_difference`, `value_ratio`, `category_match`, `brand_match`, `proposer_avg_rating`, `receiver_avg_rating`.

### Part D — Smart 2-Way Swap Compatibility Scoring
- **Endpoint:** `POST /api/swaps/compatibility`
- **Scoring Range:** Normalized 0–100 scale computed from value parity, category overlap, brand match, and user reputation scores.
- **Validation Rules:** Prevents self-swapping (same user), invalid/expired coupons, or missing items.

### Part E — 3-Way / Multi-User Swap Cycle Detection
- **Endpoint:** `GET /api/swaps/cycles`
- **Engine:** Network Graph Analysis using `networkx` (`DiGraph`).
- **Mechanism:** Builds directed demand graph where edges represent active coupon requests/wants between users. Detects elementary 3-node circular chains ($A \rightarrow B \rightarrow C \rightarrow A$) enabling zero-waste multi-party barter settlements.

### Part F — Fraud / User Anomaly Detection
- **Endpoint:** `GET /api/predictions/anomalies`
- **Artifact:** `models/anomaly_model.joblib`
- **Model Type:** `IsolationForest` (contamination rate = 5%).
- **Telemetry Monitored:** User activity vectors including view counts, request ratios, swap frequency, usage patterns, and average ratings received.
- **Output:** Detected 25 potential anomalous user accounts (5.0% of user population) for admin review.

### Part G — Category Demand Forecasting
- **Endpoint:** `POST /api/predictions/demand`
- **Artifact:** `models/demand_model.joblib`
- **Model Type:** `RandomForestRegressor`
- **Performance Metrics:**
  - **Mean Absolute Error (MAE):** 1.8130
  - **Root Mean Squared Error (RMSE):** 2.2172
- **Functionality:** Projects next-month coupon request volumes given category historical request momentum.

### Part H — System Notifications API
- **Endpoints:** `POST /api/notifications`, `GET /api/notifications`, `PUT /api/notifications/<id>/read`
- **Types Supported:** `SWAP_PROPOSAL`, `SWAP_ACCEPTED`, `SWAP_REJECTED`, `SWAP_COMPLETED`, `COUPON_EXPIRING`, `SMART_MATCH_FOUND`, `SYSTEM_ALERT`.

---

## Verification & Test Results

All 12 automated unit tests across Phase 6 and Phase 7 pass cleanly:

```
tests/test_phase6.py ....                                                [ 33%]
tests/test_phase7.py ........                                            [100%]

============================= 12 passed in 6.34s ==============================
```

- **Data Integrity:** `data/raw/*.csv` (18/18 validation checks pass) and `data/processed/*.csv` (12/12 validation checks pass) remain 100% untouched.
- **Database Schema:** `database/schema.sql` unchanged and strictly adhered to.

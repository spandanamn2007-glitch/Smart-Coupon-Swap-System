# Smart Coupon Swap System

> **An Intelligent Data Science, Machine Learning, and Full-Stack Python Platform for Peer-to-Peer Coupon Exchange**

[![Phase Status](https://img.shields.io/badge/Current_Phase-Phase_8_Final_Documentation-green)](#current-development-status)
[![License](https://img.shields.io/badge/License-Academic_Project-lightgrey)](#license)
[![Python Version](https://img.shields.io/badge/Python-3.x-brightgreen)](#technology-stack)

---

## 1. Current Development Status

**CURRENT STATUS: PHASE 8/8 — TESTING, SECURITY, DEPLOYMENT & FINAL DOCUMENTATION (COMPLETED – DEPLOYMENT PENDING)**

This project is engineered phase-by-phase using the **Reduced 8-Phase Project Plan**. Phase 1 (Planning & Architecture), Phase 2 (Database Design & MySQL), Phase 3 (Dataset Generation), Phase 4 (Data Cleaning), Phase 5 (EDA), Phase 6 (Feature Engineering & Auth), and Phase 7 (Core Platform Features & Data Science Integration) are complete.

- **Marketplace & Search (Part A):** Full CRUD for coupon listings (`/api/coupons`) with dynamic multi-parameter SQL search and authorization boundary enforcement.
- **Explainable Recommendations (Part B):** Rule-based recommendation engine (`/api/recommendations`) combining category alignment, brand affinity, discount thresholds, and seller reputation with explainability reasons.
- **Swap Acceptance Prediction (Part C):** `RandomForestClassifier` (`models/acceptance_model.joblib`) predicting barter acceptance probability (`/api/predictions/acceptance`).
- **Smart 2-Way Swap Compatibility (Part D):** 0–100 compatibility scoring engine (`/api/swaps/compatibility`) evaluating value parity, category overlap, and user ratings.
- **3-Way Multi-User Swap Cycle Graph Engine (Part E):** Network graph analysis using `networkx` (`/api/swaps/cycles`) detecting 3-node circular swap chains ($A \rightarrow B \rightarrow C \rightarrow A$).
- **Fraud & Anomaly Detection (Part F):** `IsolationForest` (`models/anomaly_model.joblib`) identifying potential anomalous user behavior patterns (`/api/predictions/anomalies`).
- **Category Demand Forecasting (Part G):** `RandomForestRegressor` (`models/demand_model.joblib`) projecting next-month request demand (`/api/predictions/demand`).
- **System Notifications (Part H):** Notification service (`/api/notifications`) handling alerts and swap match notifications.
- **Automated Testing:** `python -m pytest tests/test_phase6.py tests/test_phase7.py` verified 12/12 test suites (100% pass).

**Phase 8/8 (Testing, Security, Deployment & Final Documentation) is now implemented.**

---

## 2. Project Overview & Problem Statement

Millions of consumers receive promotional coupons, discount vouchers, and gift codes from e-commerce platforms, payment gateways, and retail brands. Many of these promotional assets may expire unused because the recipient does not intend to shop with that particular brand or category, while another consumer may actively seek a discount for that merchant.

The Smart Coupon Swap System addresses this problem by creating a structured peer-to-peer coupon exchange platform.

The system uses Data Science, Machine Learning, and Graph Theory to support coupon recommendations, acceptance prediction, explainable swap compatibility, demand prediction, anomaly detection, and multi-user swap opportunities.

---

## 3. Core Objectives

1. **Coupon Exchange Platform:** Build a secure platform connecting users who want to exchange coupons.
2. **Lifecycle Management:** Enable users to catalog, track, and manage coupons and validity dates.
3. **Personalized Recommendations:** Recommend relevant coupons using recommendation techniques.
4. **Acceptance Likelihood Prediction:** Predict whether a user is likely to accept a proposed coupon swap.
5. **Compatible Bilateral Swap Matching:** Compute explainable swap compatibility scores.
6. **Multi-User Swap Detection:** Use exchange graphs to identify circular swap opportunities.

---

## 4. Technology Stack

- Python 3.x
- MySQL 8.x
- Flask 2.3+
- PyMySQL 1.1+
- NetworkX 3.x
- scikit-learn 1.6+
- Joblib 1.4+
- Werkzeug (Secure Password Hashing)
- python-dotenv
- HTML/CSS/JavaScript
- Bootstrap
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Pytest
- Git and GitHub

---

## 5. Database

Database name: `smart_coupon_swap`  
Database engine: MySQL 8.x with InnoDB and utf8mb4.

The database contains 17 tables covering:
- Access control (`roles`, `users`)
- User preferences (`user_general_preferences`, `user_category_preferences`, `user_brand_preferences`)
- Coupon categories and brands (`categories`, `brands`)
- Coupon records (`coupons`)
- Behavioral telemetry (`coupon_views`)
- Coupon requests and usage (`coupon_requests`, `coupon_usage`)
- Swaps and swap history (`swaps`, `swap_items`, `swap_history`)
- Ratings, Reports, Notifications (`ratings`, `reports`, `notifications`)

---

## 6. How to Run Backend & Tests

### Start Flask Server
```bash
python run.py
```
*App will start on `http://localhost:5000`*

### Health Check
```bash
curl http://localhost:5000/health
```

### Train ML Models
```bash
python scripts/train_models.py
```

### Run Automated Tests
```bash
python -m pytest tests/test_phase6.py tests/test_phase7.py tests/test_phase8.py
```

---

## 7. Reduced 8-Phase Project Roadmap

- [x] Phase 1 — Project Planning, Requirements & Architecture
- [x] Phase 2 — Database Design & MySQL Implementation
- [x] Phase 3 — Dataset Generation / Collection
- [x] Phase 4 — Data Cleaning & Preprocessing
- [x] Phase 5 — Exploratory Data Analysis (EDA)
- [x] Phase 6 — Feature Engineering + Flask Backend + Authentication (Phase 6/8)
- [x] Phase 7 — Core Platform Features & Data Science Integration (Phase 7/8)
- [x] Phase 8 — Testing, Security, Deployment & Final Documentation (Phase 8/8)

---

## 8. Current Phase Boundary

Phase 7/8 is complete.

Phase 8/8 (Testing, Security, Deployment & Final Documentation) is now complete. Deployment preparation/documentation is ready, but actual deployment has not yet occurred.

---

## 9. Phase 8 – Testing, Security, Deployment & Final Documentation

The following components have been implemented in Phase 8:

- **User Dashboard** – Provides personalized coupon statistics, active coupons, and request history.
- **Analytics Dashboard** – Admin‑only view with system‑wide metrics and usage analytics.
- **Admin Dashboard** – Administrative console for managing users, coupons, and system settings.
- **Dashboard & Admin Routes** – New Flask blueprints (`/api/dashboard/*` and `/api/admin/*`) with proper authentication and authorization guards.
- **Phase 8 Test Suite** – 43 automated tests covering dashboard endpoints, security checks, and deployment scripts.
- **Deployment Guide** – Updated `docs/deployment‑guide.md` describing environment setup, production server configuration, and a security checklist.
- **Final Testing & Security Preparation** – Security audit scripts, hardening recommendations, and final verification steps (deployment itself not performed).

Deployment to a production environment has not been performed; the guide and preparation steps are ready for future rollout.

---

## 10. Project Documentation

- [Project Overview](docs/project-overview.md)
- [Software Requirements Specification](docs/requirements.md)
- [System Architecture & Technical Specification](docs/architecture.md)
- [Database Design Specification](docs/database-design.md)
- [Database ERD](docs/database-erd.md)
- [Database Setup & Operations Guide](database/README.md)
- [Dataset Design Specification](docs/dataset-design.md)
- [Data Cleaning & Preprocessing Report](docs/data-cleaning-report.md)
- [Exploratory Data Analysis Report](docs/eda-report.md)
- [Feature Engineering Specification & Report](docs/feature-engineering-report.md)
- [Phase 7 Core Platform & Data Science Report](docs/phase7-core-platform-report.md)

---

## 11. Development Principles

- Phase-by-phase development with explicit approval gates
- No implementation of future phases before approval
- No fake ML metrics or invented results
- No hardcoded prediction results
- Secure handling of credentials and secrets
- Modular and maintainable architecture
- Reproducible data science workflow

---

## 12. License

Academic Project.

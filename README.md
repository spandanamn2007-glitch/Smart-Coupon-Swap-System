# Smart Coupon Swap System

> **An Intelligent Data Science, Machine Learning, and Full-Stack Python Platform for Peer-to-Peer Coupon Exchange**

[![Phase Status](https://img.shields.io/badge/Current_Phase-Phase_6_Feature_Engineering_Backend_Auth-blue)](#current-development-status)
[![License](https://img.shields.io/badge/License-Academic_Project-lightgrey)](#license)
[![Python Version](https://img.shields.io/badge/Python-3.x-brightgreen)](#technology-stack)

---

## 1. Current Development Status

**CURRENT STATUS: PHASE 6/8 — FEATURE ENGINEERING + FLASK BACKEND + AUTHENTICATION (COMPLETE)**

This project is engineered phase-by-phase using the **Reduced 8-Phase Project Plan**. Phase 1 (Planning & Architecture), Phase 2 (Database Design & MySQL), Phase 3 (Dataset Generation), Phase 4 (Data Cleaning), Phase 5 (Exploratory Data Analysis), and Phase 6 (Feature Engineering + Flask Backend + Authentication) are complete.

- **Feature Engineering (Part A):** Pipeline `scripts/feature_engineering.py` extracts 4 feature datasets (`user_features`, `coupon_features`, `interaction_features`, `swap_pair_features`) in `data/features/`, fully documented in `docs/feature-engineering-report.md`.
- **Flask Backend Foundation (Part B):** Application factory in `app/`, database layer `app/services/db.py` connecting securely to MySQL `smart_coupon_swap`, and `/health` status endpoint.
- **Authentication & User Profiles (Part C):** User registration (`POST /api/auth/register`), login (`POST /api/auth/login`), logout (`POST /api/auth/logout`), session verification (`GET /api/auth/me`), profile operations (`GET/PUT /api/users/profile`), and preference management (`GET/PUT /api/users/preferences`) with strict authorization boundary enforcement and Werkzeug password hashing.
- **Automated Testing:** `python -m pytest tests/test_phase6.py` verified 4/4 test suites (100% pass).

**Academic Notice:** All datasets are synthetic for academic and experimental software engineering. Raw data (`data/raw/`) and processed data (`data/processed/`) remain preserved.

No coupon marketplace, recommendation engine, predictive models, swap matching engines, or frontend UI have been implemented yet.

---

## 2. Project Overview & Problem Statement

Millions of consumers receive promotional coupons, discount vouchers, and gift codes from e-commerce platforms, payment gateways, and retail brands. Many of these promotional assets may expire unused because the recipient does not intend to shop with that particular brand or category, while another consumer may actively seek a discount for that merchant.

The Smart Coupon Swap System addresses this problem by creating a structured peer-to-peer coupon exchange platform.

The planned system will use Data Science, Machine Learning, and Graph Theory to support coupon recommendations, acceptance prediction, explainable swap compatibility, demand prediction, anomaly detection, and multi-user swap opportunities.

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
- Werkzeug (Secure Password Hashing)
- python-dotenv
- HTML/CSS/JavaScript
- Bootstrap
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- scikit-learn
- Joblib
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

### Run Feature Engineering
```bash
python scripts/feature_engineering.py
```

### Run Automated Tests
```bash
python -m pytest tests/test_phase6.py
```

---

## 7. Reduced 8-Phase Project Roadmap

- [x] Phase 1 — Project Planning, Requirements & Architecture
- [x] Phase 2 — Database Design & MySQL Implementation
- [x] Phase 3 — Dataset Generation / Collection
- [x] Phase 4 — Data Cleaning & Preprocessing
- [x] Phase 5 — Exploratory Data Analysis (EDA)
- [x] Phase 6 — Feature Engineering + Flask Backend + Authentication (Phase 6/8)
- [ ] Phase 7 — Core Platform Features & Data Science Integration (Phase 7/8)
- [ ] Phase 8 — Testing, Security, Deployment & Final Documentation (Phase 8/8)

---

## 8. Current Phase Boundary

Phase 6/8 is complete.

Phase 7/8 (Core Platform Features & Data Science Integration) has NOT started.

No coupon marketplace UI, recommendation algorithms, ML predictive models, bilateral swap engines, circular swap graph algorithms, or cloud deployment infrastructure are implemented.

---

## 9. Project Documentation

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

---

## 10. Development Principles

- Phase-by-phase development with explicit approval gates
- No implementation of future phases before approval
- No fake ML metrics or invented results
- No hardcoded prediction results
- Secure handling of credentials and secrets
- Modular and maintainable architecture
- Reproducible data science workflow

---

## 11. License

Academic Project.

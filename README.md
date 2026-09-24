# Smart Coupon Swap System

> **An Intelligent Data Science, Machine Learning, and Full-Stack Python Platform for Peer-to-Peer Coupon Exchange**

[![Phase Status](https://img.shields.io/badge/Current_Phase-Phase_3_Dataset_Generation-blue)](#current-development-status)
[![License](https://img.shields.io/badge/License-Academic_Project-lightgrey)](#license)
[![Python Version](https://img.shields.io/badge/Python-3.x-brightgreen)](#technology-stack)

---

## 1. Current Development Status

**CURRENT STATUS: PHASE 3 — DATASET GENERATION / COLLECTION (COMPLETE)**

This project is being engineered strictly phase-by-phase. Phase 1 (Project Planning & Architecture), Phase 2 (Database Design & MySQL Implementation), and Phase 3 (Dataset Generation / Collection) are complete.

All 10 Phase 3 raw CSV datasets have been generated using a deterministic script (`scripts/generate_datasets.py`, seed = 42) and verified using an automated integrity suite (`scripts/validate_datasets.py`, 18/18 checks passed).

**Academic Notice:** All generated datasets are entirely synthetic and constructed strictly for academic and experimental software development purposes. No real personal identifiers, proprietary merchant data, or live coupon codes are utilized.

No data cleaning, data preprocessing, feature engineering, machine learning models, Flask routes, or frontend interfaces have been implemented yet.

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
- Flask
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

Only technologies relevant to completed phases should be described as active.

---

## 5. Database

Database name: `smart_coupon_swap`  
Database engine: MySQL 8.x with InnoDB and utf8mb4.

The database contains 17 tables covering:
- Access control
- Users and profiles
- User preferences
- Coupon categories and brands
- Coupon records
- Behavioral telemetry
- Coupon requests and usage
- Swaps and swap history
- Ratings
- Reports
- Notifications

---

## 6. Raw Datasets (Phase 3)

All raw datasets are located in `data/raw/` and generated deterministically (`SEED = 42`):

| File Name | Records | Description |
|---|---|---|
| `categories.csv` | 10 | Retail vertical taxonomy |
| `brands.csv` | 36 | Synthetic brand definitions linked to categories |
| `users.csv` | 500 | User demographic profiles and discount affinities |
| `coupons.csv` | 2,500 | Coupon listings with discount values and validity |
| `user_preferences.csv` | 1,282 | Explicit user category and brand preferences |
| `coupon_views.csv` | 5,000 | User clickstream and dwell-time telemetry |
| `coupon_requests.csv` | 1,500 | Unilateral coupon acquisition requests |
| `coupon_usage.csv` | 1,000 | Voucher lifecycle closure (used, expired, cancelled) |
| `swaps.csv` | 500 | Bilateral exchange proposals and outcomes |
| `ratings.csv` | 401 | Post-swap counterparty reviews and scores (1–5) |

---

## 7. Project Roadmap

- [x] Phase 1 — Project Planning, Requirements & Architecture
- [x] Phase 2 — Database Design & MySQL
- [x] Phase 3 — Dataset Generation / Collection
- [ ] Phase 4 — Data Cleaning & Preprocessing
- [ ] Phase 5 — Exploratory Data Analysis
- [ ] Phase 6 — Feature Engineering
- [ ] Phase 7 — Flask Backend Foundation
- [ ] Phase 8 — Authentication & User Profiles
- [ ] Phase 9 — Coupon Management & Marketplace
- [ ] Phase 10 — Recommendation System
- [ ] Phase 11 — Coupon Acceptance Prediction
- [ ] Phase 12 — Smart Two-Way Swap Engine
- [ ] Phase 13 — Multi-User / Three-Way Swap Detection
- [ ] Phase 14 — Demand Prediction & Anomaly Detection
- [ ] Phase 15 — User & Admin Dashboards
- [ ] Phase 16 — Testing, Security & Optimization
- [ ] Phase 17 — GitHub, Deployment & Final Documentation

---

## 8. Current Phase Boundary

Phase 3 is complete.

Phase 4 (Data Cleaning & Preprocessing) has NOT started.

No data transformations, feature matrices, machine learning models, Flask routes, frontend pages, recommendations, prediction results, or cloud deployments are implemented.

---

## 9. Project Documentation

- [Project Overview](docs/project-overview.md)
- [Software Requirements Specification](docs/requirements.md)
- [System Architecture & Technical Specification](docs/architecture.md)
- [Database Design Specification](docs/database-design.md)
- [Database ERD](docs/database-erd.md)
- [Database Setup & Operations Guide](database/README.md)
- [Dataset Design Specification](docs/dataset-design.md)

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

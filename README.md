# Smart Coupon Swap System

> **An Intelligent Data Science, Machine Learning, and Full-Stack Python Platform for Peer-to-Peer Coupon Exchange**

[![Phase Status](https://img.shields.io/badge/Current_Phase-Phase_2_Database_Design-blue)](#current-development-status)
[![License](https://img.shields.io/badge/License-Academic_Project-lightgrey)](#license)
[![Python Version](https://img.shields.io/badge/Python-3.x-brightgreen)](#technology-stack)

---

## 1. Current Development Status

**CURRENT STATUS: PHASE 2 — DATABASE DESIGN & MYSQL (COMPLETE)**

This project is being engineered strictly phase-by-phase. Phase 1 (Project Planning & Architecture) and Phase 2 (Database Design & MySQL Implementation) are complete.

The relational database contains 17 tables designed for the Smart Coupon Swap System. The database schema, seed/reference data, and integrity validation have been implemented and verified on MySQL 8.x.

No backend routes, frontend interfaces, or machine learning models have been implemented yet.

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

Only technologies relevant to the completed/current phase should be described as implemented.

---

## 5. Database

Database name:

`smart_coupon_swap`

Database engine:

MySQL 8.x with InnoDB and utf8mb4.

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

## 6. Database Tables

1. roles
2. users
3. categories
4. brands
5. coupons
6. user_category_preferences
7. user_brand_preferences
8. user_general_preferences
9. coupon_views
10. coupon_requests
11. coupon_usage
12. swaps
13. swap_items
14. swap_history
15. ratings
16. reports
17. notifications

---

## 7. Project Roadmap

- [x] Phase 1 — Project Planning, Requirements & Architecture
- [x] Phase 2 — Database Design & MySQL
- [ ] Phase 3 — Dataset Generation / Collection
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

## 8. Phase 2 Files

The following files were created as part of Phase 2:

- `database/schema.sql` — Full 17-table DDL for MySQL 8.x
- `database/seed.sql` — Reference data: 2 roles, 8 categories, 10 brands, 3 test users
- `database/README.md` — MySQL Workbench and CLI setup instructions
- `docs/database-design.md` — Database design specification and ML integration notes
- `docs/database-erd.md` — Mermaid ER diagram matching the schema
- `scripts/validate_database.py` — Automated validation script (8 tests)
- `.env.example` — Safe configuration template with no real credentials
- `.gitignore` — Excludes `.env`, `__pycache__`, and other non-tracked files

---

## 9. Phase 2 Validation

The validation script `scripts/validate_database.py` connects to the local MySQL instance and verifies:

- All 17 tables exist
- Foreign key rejection on invalid owner_id
- Unique constraint on duplicate email
- CHECK constraint on discount_value
- CHECK constraint on expiry_date before issue_date
- Self-rating prevention (rater_id = rated_user_id)
- Unique constraint on duplicate swap rating
- Full drop and recreate of schema and seed data

Validation was executed successfully against MySQL 8.0.45 on the local development machine.

---

## 10. Current Phase Boundary

Phase 2 is complete.

Phase 3 has NOT started.

Datasets, preprocessing, EDA, feature engineering, machine learning models, Flask routes, frontend pages, recommendations, prediction results, and deployment are not yet implemented.

---

## 11. Project Documentation

- [Project Overview](docs/project-overview.md)
- [Software Requirements Specification](docs/requirements.md)
- [System Architecture & Technical Specification](docs/architecture.md)
- [Database Design Specification](docs/database-design.md)
- [Database ERD](docs/database-erd.md)
- [Database Setup & Operations Guide](database/README.md)

---

## 12. Development Principles

- Phase-by-phase development with explicit approval gates
- No implementation of future phases before approval
- No fake ML metrics or invented results
- No hardcoded prediction results
- Secure handling of credentials and secrets
- Modular and maintainable architecture
- Reproducible data science workflow

---

## 13. License

Academic Project.

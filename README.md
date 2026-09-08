# Smart Coupon Swap System

> **An Intelligent Data Science, Machine Learning, and Full-Stack Python Platform for Peer-to-Peer Coupon Exchange**

[![Phase Status](https://img.shields.io/badge/Current_Phase-Phase_1_Planning_Architecture-blue)](#current-development-status)
[![License](https://img.shields.io/badge/License-Academic_Project-lightgrey)](#license)
[![Python Version](https://img.shields.io/badge/Python-3.x-brightgreen)](#technology-stack)

---

## 1. Current Development Status

**CURRENT STATUS: PHASE 1 — PROJECT PLANNING, REQUIREMENTS & ARCHITECTURE (COMPLETE)**

This project is being engineered strictly phase-by-phase. Phase 1 covers project planning, requirements, architecture, data science planning, database entity planning, and the overall implementation roadmap.

No database, backend routes, frontend interfaces, ML models, or fake evaluation metrics have been implemented yet.

---

## 2. Project Overview & Problem Statement

Millions of consumers receive promotional coupons, discount vouchers, and gift codes from e-commerce platforms, payment gateways, and retail brands. However, many of these promotional assets expire unused because the recipient does not intend to shop with that particular brand or category. At the same time, another consumer may actively seek a discount for that merchant.

Due to the absence of a dedicated, secure, and intelligent exchange platform, users may abandon unused vouchers or rely on informal exchange methods, resulting in significant wasted promotional value.

The Smart Coupon Swap System addresses this problem by creating a structured peer-to-peer coupon exchange platform. Using Data Science, Machine Learning, and Graph Theory, the system will eventually recommend relevant coupons, predict acceptance likelihood, calculate explainable swap compatibility, forecast demand, detect suspicious activity, and identify multi-user circular swap opportunities.

---

## 3. Core Objectives

1. **Coupon Exchange Platform:** Build a secure web platform connecting users who want to exchange coupons.

2. **Lifecycle Management:** Enable users to catalog, track, and manage unused coupons and validity dates.

3. **Personalized Recommendations:** Recommend relevant coupons using content-based and hybrid recommendation techniques.

4. **Acceptance Likelihood Prediction:** Predict whether a user is likely to accept a proposed coupon swap.

5. **Compatible Bilateral Swap Matching:** Compute explainable swap compatibility scores from 0–100%.

6. **Multi-User Swap Detection:** Use exchange graphs to identify 3-way circular swap chains such as A → B → C → A.

7. **Coupon Demand Prediction:** Classify coupons into High, Medium, and Low demand tiers.

8. **Suspicious Activity & Anomaly Detection:** Flag abnormal listing behavior and potential abuse using unsupervised learning.

9. **Analytical Dashboards:** Provide interactive analytical dashboards for users and administrators.

10. **Administrative Moderation:** Provide governance tools for reviewing reports, disputes, and suspicious activity.

11. **End-to-End Data Science Lifecycle:** Demonstrate a reproducible workflow from data collection and preprocessing through model training, evaluation, prediction, and application integration.

---

## 4. Technology Stack

- Python 3.x
- Flask
- HTML5
- CSS3
- JavaScript
- Bootstrap
- MySQL
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly
- Scikit-learn
- Joblib
- Pytest
- Git and GitHub

Deployment technologies will be selected during the final deployment phase.

---

## 5. Planned Data Science & Machine Learning Components

The planned data science pipeline is:

Raw Data → Data Collection/Generation → Data Cleaning → Preprocessing → Exploratory Data Analysis → Feature Engineering → Model Training → Evaluation → Prediction → Application Integration

Planned ML components include:

- Coupon recommendation
- Coupon acceptance prediction
- Coupon demand prediction
- Anomaly detection
- Smart coupon swap compatibility
- Multi-user swap detection using graph concepts

No ML model is being implemented in Phase 1.

---

## 6. Planned User Features

- User registration and login
- User profile and preferences
- Coupon listing
- Coupon search and filtering
- Coupon expiry tracking
- Coupon requests
- Coupon exchange
- Swap history
- Ratings
- Reports
- Notifications

---

## 7. Planned Administrative Features

- User management
- Coupon moderation
- Report and dispute management
- Suspicious activity review
- Analytics dashboard
- Model and system monitoring

---

## 8. Planned Database Entities

The conceptual database will contain entities such as:

- Users
- Roles
- Categories
- Brands
- Coupons
- User Preferences
- Coupon Views
- Coupon Requests
- Coupon Usage
- Swaps
- Swap History
- Ratings
- Reports
- Notifications

The actual database schema and SQL implementation will be created in Phase 2.

---

## 9. System Architecture

The planned architecture follows:

User → Frontend → Flask Backend / REST API → Service Layer → Database

The backend will eventually integrate services for:

- User Management
- Coupon Management
- Recommendation Engine
- ML Prediction Engine
- Smart Swap Engine
- Demand Prediction Engine
- Anomaly Detection Engine
- Notification Service

Detailed architecture documentation is available in `docs/architecture.md`.

---

## 10. Development Roadmap

- [x] Phase 1 — Project Planning, Requirements & Architecture
- [ ] Phase 2 — Database Design & MySQL
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

## 11. Phase 1 Documentation

- [Project Overview](docs/project-overview.md)
- [Software Requirements Specification](docs/requirements.md)
- [System Architecture & Technical Specification](docs/architecture.md)

---

## 12. Development Principles

- Phase-by-phase development
- Modular and maintainable architecture
- Testable components
- Explainable machine learning
- Reproducible data science workflow
- No fake ML metrics
- No hardcoded prediction results
- Secure handling of credentials and secrets
- No implementation of future phases before approval

---

## 13. License

Academic Project.

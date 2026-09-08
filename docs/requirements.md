# Software Requirements Specification (SRS)

## Smart Coupon Swap System
**Document Version**: 1.0  
**Project Phase**: Phase 1 — Project Planning, Requirements & Architecture  
**Status**: Approved for Baseline  

---

## 1. Functional Requirements (FR)

The functional requirements specify the software capabilities, operations, and behaviors that the Smart Coupon Swap System must execute.

### 1.1 Module 1: User Management & Authentication
* **FR-1.1 User Registration**: The system shall allow new users to register by providing first name, last name, unique email address, mobile number (optional), and a secure password.
* **FR-1.2 Secure Authentication**: The system shall authenticate registered users using encrypted credentials (hashed using bcrypt/argon2 with salt). The system shall support session generation, remember-me options, and secure logout.
* **FR-1.3 Profile & Preference Management**: The system shall allow users to view and edit profile details, specify preferred shopping categories (e.g., Electronics, Fashion, Food, Travel, Groceries), select favored brands, and establish notification preferences.
* **FR-1.4 User Dashboard & Activity Ledger**: The system shall provide each user with a personal dashboard displaying active owned coupons, pending swap requests, accepted/completed swaps, historical swaps, and reputation ratings.

### 1.2 Module 2: Coupon Management
* **FR-2.1 Coupon Cataloging**: The system shall enable authenticated users to add unused coupons by specifying:
  * Title and description
  * Merchant/Brand (e.g., Amazon, Myntra, Swiggy, Uber)
  * Category (e.g., Fashion, Food, Electronics, Travel)
  * Coupon code (stored encrypted/masked until swap completion)
  * Discount type (percentage, flat amount, cashback)
  * Discount value and minimum purchase threshold
  * Expiration date and time
  * Terms and conditions / usage constraints
* **FR-2.2 Coupon Lifecycle Management**: The system shall track and update coupon statuses through:
  * `AVAILABLE`: Active and discoverable in the marketplace.
  * `PENDING_SWAP`: Locked in an active swap negotiation.
  * `SWAPPED`: Successfully transferred to a counterparty.
  * `EXPIRED`: Past expiration date, automatically filtered out from active marketplace.
  * `FLAGGED`: Under administrative review due to reports.
* **FR-2.3 Modification and Deletion**: The system shall allow coupon owners to edit metadata or delete coupons, provided the coupon is not currently engaged in a pending swap transaction.
* **FR-2.4 Expiry Auto-Tracking**: The system shall periodically assess coupon expiration dates and transition overdue coupons to `EXPIRED` status.

### 1.3 Module 3: Marketplace & Discovery
* **FR-3.1 Coupon Browsing**: The system shall provide a public marketplace where users can browse all `AVAILABLE` coupons with pagination.
* **FR-3.2 Multi-Parameter Search & Filtering**: The system shall enable searching and filtering by:
  * Keyword search (title, brand name, description)
  * Category multi-select
  * Brand multi-select
  * Discount range (minimum discount percentage or amount)
  * Validity / Days until expiry
* **FR-3.3 Sorting Mechanisms**: The system shall allow sorting results by:
  * Highest discount value
  * Shortest days remaining to expiry (urgency)
  * Popularity / demand level
  * Recommended for you (personalized score)
* **FR-3.4 Coupon Detail View**: The system shall show detailed coupon terms, merchant branding, days until expiry, and the owner's public reputation score without exposing the secret coupon code.

### 1.4 Module 4: Swap Request Management
* **FR-4.1 Swap Proposal Creation**: An authenticated user (User A) viewing User B's available coupon shall be able to initiate a swap request by proposing one of their own available coupons in return.
* **FR-4.2 Swap Negotiation Workflow**:
  * User B receives notification of the incoming proposal.
  * User B can view the proposed coupon details and compatibility score.
  * User B can **Accept** or **Reject** the proposal.
  * User A can **Cancel** the pending proposal before User B responds.
* **FR-4.3 Mutual Code Release**: Upon acceptance by User B, the system shall atomically mark both coupons as `SWAPPED`, record the swap event in the historical ledger, and securely reveal the respective coupon codes/vouchers to both counterparties.

### 1.5 Module 5: Smart Two-Way Swap Engine
* **FR-5.1 Bilateral Match Discovery**: For any user browsing the marketplace or viewing a coupon, the system shall automatically detect if the user owns a coupon that the counterparty would likely desire.
* **FR-5.2 Multi-Factor Compatibility Scoring**: The system shall calculate an explainable compatibility score ($S \in [0, 100\%]$) evaluated using:
  * Category preference alignment ($w_{cat}$)
  * Brand affinity alignment ($w_{brand}$)
  * Economic discount value parity ($w_{val}$)
  * Expiry urgency synchronization ($w_{exp}$)
  * Historical counterparty interaction affinity ($w_{hist}$)
* **FR-5.3 Explainable Compatibility Breakdown**: The system shall provide the user with human-readable rationale (e.g., "92% Compatibility: Perfect Brand Match (Amazon ↔ Myntra), Equal Value ($20 equivalent), Balanced Expiration").

### 1.6 Module 6: Multi-User / Three-Way Swap Detection
* **FR-6.1 Swap Desire Graph Construction**: The system shall construct a directed multi-user swap graph $G = (V, E)$ where nodes $V$ represent users/coupons and directed edges $E$ represent stated desires or preference matches ($User_i \xrightarrow{desires} Coupon_j$).
* **FR-6.2 Circular Loop Detection (3-Way Swaps)**: The system shall execute graph cycle detection algorithms to discover 3-way circular barter chains ($User_A \xrightarrow{gives} User_B \xrightarrow{gives} User_C \xrightarrow{gives} User_A$).
* **FR-6.3 Multi-Party Proposal & Atomic Commitment**: When a 3-way cycle is detected, the system shall notify all three participants. Upon unanimous three-party approval, the system shall execute an atomic three-way database transaction transferring all three vouchers simultaneously.

### 1.7 Module 7: Machine Learning — Coupon Acceptance Prediction
* **FR-7.1 Acceptance Probability Estimation**: The system shall utilize a trained supervised machine learning model to estimate the conditional probability $P(\text{Accept} = 1 \mid \text{User}, \text{Coupon}, \text{Context})$ that a user will accept a proposed coupon swap.
* **FR-7.2 Feature-Based Inference**: The model shall evaluate tabular features including user historical acceptance rates, category affinity, brand loyalty index, discount magnitude, relative savings ratio, and temporal buffer before expiration.
* **FR-7.3 Recommendation Prioritization**: Predicted acceptance probabilities shall be incorporated as a ranking signal in swap proposal sorting.

### 1.8 Module 8: Machine Learning — Coupon Recommendation System
* **FR-8.1 Content-Based Filtering**: The system shall construct numerical feature vectors for coupons (category one-hot, brand embedding, discount normalized, validity days) and user preference vectors. It shall compute cosine similarity to rank top-$K$ recommended coupons.
* **FR-8.2 Collaborative Filtering Investigation**: When interaction matrices (views, clicks, requests) achieve sufficient density, the system shall test matrix factorization / user-item collaborative filtering.
* **FR-8.3 Personalized Discovery Feed**: Display a curated "Recommended For You" carousel on the user's dashboard.

### 1.9 Module 9: Machine Learning — Coupon Demand Prediction
* **FR-9.1 Demand Classification**: The system shall predict the market demand level of newly cataloged or existing coupons categorized into `High`, `Medium`, and `Low`.
* **FR-9.2 Telemetry Feature Integration**: Demand modeling shall consume behavioral signals: cumulative views, click-through rates, swap request counts, discount depth, merchant market share, and remaining lifespan.
* **FR-9.3 Visual Demand Indicators**: Display dynamic demand badges in the marketplace to inform trading decisions.

### 1.10 Module 10: Machine Learning — Anomaly & Fraud Detection
* **FR-10.1 Outlier & Abuse Detection**: The system shall apply unsupervised anomaly detection (e.g., Isolation Forest / Local Outlier Factor) to identify suspicious behavior patterns:
  * Abnormally high listing velocity (potential bot spamming)
  * Repetitive listing of identical coupon codes across multiple accounts
  * Unusually rapid request-cancel cycles
  * Mismatched category-brand anomalies
* **FR-10.2 Administrative Flagging**: The system shall route detected anomalies to an administrative moderation queue for human-in-the-loop review rather than executing punitive actions autonomously.

### 1.11 Module 11: Rating, Reviews & Trust Score
* **FR-11.1 Post-Swap Evaluation**: Following a completed swap, both counterparties shall be prompted to rate the exchange (1 to 5 stars) and indicate whether the coupon code redeemed successfully.
* **FR-11.2 User Reputation Score**: The system shall calculate an aggregate public trust score for each user reflecting their swap history, successful redemptions, and peer ratings.

### 1.12 Module 12: Reporting & Content Moderation
* **FR-12.1 Reporting System**: Users shall be able to flag coupons (e.g., "Already Redeemed / Invalid Code", "Misleading Information", "Expired", "Prohibited Content") or report abusive users.
* **FR-12.2 Moderation Workflow**: Flagged items shall trigger an administrative alert and update the coupon state if report thresholds are exceeded.

### 1.13 Module 13: Notification System
* **FR-13.1 Real-Time In-App Alerts**: The system shall generate notifications for:
  * Incoming swap requests
  * Acceptance or rejection of proposed swaps
  * Newly discovered 2-way and 3-way smart swap matches
  * Impending coupon expiration (e.g., 48 hours remaining)
  * System administrative updates

### 1.14 Module 14: Administrative Management & Analytics
* **FR-14.1 User Governance**: Admins can search, view, suspend, or reactivate user accounts.
* **FR-14.2 Coupon Moderation**: Admins can inspect active listings, modify flagged states, or purge fraudulent listings.
* **FR-14.3 Analytical Dashboard**: Display visual aggregations of platform metrics: total users, active listings, swap conversion rates, category liquidity, brand popularity, and ML model inference summaries.

---

## 2. Non-Functional Requirements (NFR)

Non-functional requirements describe quality attributes, system performance, security constraints, and operational criteria.

### 2.1 Security & Data Integrity (NFR-SEC)
* **NFR-SEC-1 Password Protection**: Passwords must never be stored in plain text. Passwords shall be cryptographically hashed using industry-standard hashing algorithms (bcrypt or Argon2) with per-user salt.
* **NFR-SEC-2 Sensitive Asset Protection (Code Masking)**: Promotional voucher codes, PINs, and redemption URLs must be encrypted at rest and masked in the UI. Plaintext codes shall only be rendered to verified counterparties upon atomic swap completion.
* **NFR-SEC-3 Injection Prevention**: All database queries must use parameterized statements or ORM abstractions to prevent SQL injection.
* **NFR-SEC-4 Cross-Site Scripting (XSS) & CSRF**: All user inputs rendered in HTML templates must be auto-escaped. All state-modifying POST/PUT/DELETE forms must validate unique CSRF tokens.
* **NFR-SEC-5 Session Security**: HTTP sessions must use secure flags (`HttpOnly`, `SameSite=Lax`, and `Secure` when HTTPS is configured).
* **NFR-SEC-6 Zero Plaintext Credentials in VCS**: API keys, database credentials, and cryptographic salts must reside in `.env` configuration files excluded by `.gitignore`.

### 2.2 Performance & Latency (NFR-PERF)
* **NFR-PERF-1 API Response Time**: Typical web pages (dashboard, marketplace, coupon view) must load in less than 300 ms under standard local hosting conditions.
* **NFR-PERF-2 Search & Filter Latency**: Marketplace query filtering across $10,000+$ coupon records must return results within 200 ms using database indexing on `category_id`, `brand_id`, `status`, and `expiry_date`.
* **NFR-PERF-3 ML Model Inference Latency**: Real-time batch predictions (e.g., calculating acceptance probability or scoring swap compatibility) must complete in under 150 ms per proposal.
* **NFR-PERF-4 Graph Cycle Search**: Depth-limited ($k=3$) multi-user cycle detection must execute in under 1 second for active candidate subgraphs.

### 2.3 Scalability & Modularity (NFR-SCAL)
* **NFR-SCAL-1 Layered Architecture**: The system must enforce strict separation of concerns: Presentation Layer, Routing/API Layer, Service Layer, ML Engines, and Data Access Layer.
* **NFR-SCAL-2 Decoupled ML Pipeline**: Machine learning feature transformations and model inference pipelines must be decoupled from HTTP request handling, allowing model artifacts to be re-trained offline and loaded dynamically via Joblib.
* **NFR-SCAL-3 Database Scalability**: The MySQL schema design must follow Third Normal Form (3NF) to eliminate redundancy, with foreign key indexing for high-frequency join operations.

### 2.4 Reliability & Fault Tolerance (NFR-REL)
* **NFR-REL-1 Atomic Transactions**: All coupon swap executions (both two-way bilateral and three-way circular) must be wrapped in ACID-compliant database transactions. If any party's state update fails, the entire transaction must roll back cleanly.
* **NFR-REL-2 Double-Swap Prevention**: Concurrency control (pessimistic locking via `SELECT ... FOR UPDATE` or optimistic version checking) must guarantee that a coupon cannot be simultaneously accepted in two competing swap proposals.
* **NFR-REL-3 Graceful Error Handling**: The application must catch and log operational exceptions without crashing the process, returning user-friendly error pages (HTTP 404, 500) rather than raw tracebacks.

### 2.5 Usability & Human-Centered Design (NFR-USA)
* **NFR-USA-1 Responsive Design**: The frontend interface must be fully responsive across desktop, tablet, and mobile displays using Bootstrap 5 grid systems.
* **NFR-USA-2 Explainable Intelligence**: Whenever the system presents an AI recommendation or smart swap compatibility score, it must display human-interpretable rationale (e.g., category match, brand affinity, value parity) to build user trust.
* **NFR-USA-3 Clear Feedback & Toast Alerts**: The UI must provide immediate visual confirmation (alerts, modal confirmations, badge counters) for user actions like submitting requests, reporting errors, or editing listings.

### 2.6 Maintainability & Testability (NFR-MAIN)
* **NFR-MAIN-1 Code Standards**: Python code must adhere strictly to PEP 8 style conventions with clear docstrings, modular function designs, and comprehensive comments.
* **NFR-MAIN-2 Automated Test Suite**: Critical business logic, swap transactions, and graph cycle detection algorithms must be covered by automated Pytest unit and integration tests.
* **NFR-MAIN-3 Reproducible Data Science**: All data generation, preprocessing, and model training pipelines must be scripted and version-controlled with deterministic random seeds (`random_state=42`) ensuring full reproducibility.

### 2.7 Availability & Monitoring (NFR-AVAIL)
* **NFR-AVAIL-1 Health Probes**: The system shall expose a lightweight health-check endpoint (`/health` or `/api/status`) verifying database connectivity and model availability.
* **NFR-AVAIL-2 Centralized Logging**: System events, failed authentication attempts, swap executions, and anomaly flags must be logged with timestamps and log levels (`INFO`, `WARNING`, `ERROR`).

### 2.8 Data Privacy & Ethical AI (NFR-PRIV)
* **NFR-PRIV-1 Data Minimization**: Only essential user information necessary for authentication, preference profiling, and swap communication shall be gathered.
* **NFR-PRIV-2 Algorithmic Fairness & Non-Discrimination**: Recommendation and acceptance models must evaluate transactional attributes (categories, discounts, timestamps) without relying on sensitive demographic identifiers for discriminatory filtering.
* **NFR-PRIV-3 Human-in-the-Loop Governance**: Unsupervised fraud/anomaly detection models must serve strictly as decision support tools for administrators, ensuring no user account is terminated without human review.

---

## 3. Requirements Traceability Matrix (Summary)

| Module / Area | Functional ID | Related NFR | Primary Tech Component |
| :--- | :--- | :--- | :--- |
| Authentication | FR-1.1 - 1.4 | NFR-SEC-1, NFR-SEC-5 | Flask-Login / Werkzeug / MySQL |
| Coupon Catalog | FR-2.1 - 2.4 | NFR-SEC-2, NFR-REL-2 | CouponService / MySQL |
| Marketplace | FR-3.1 - 3.4 | NFR-PERF-2, NFR-USA-1 | MarketplaceService / Jinja2 / Bootstrap |
| Swap Negotiations | FR-4.1 - 4.3 | NFR-REL-1, NFR-REL-2 | SwapService / MySQL Transactions |
| Smart Swap Engine | FR-5.1 - 5.3 | NFR-PERF-3, NFR-USA-2 | SmartSwapEngine / Python Math |
| Multi-User Swaps | FR-6.1 - 6.3 | NFR-PERF-4, NFR-REL-1 | GraphCycleDetector / NetworkX / MySQL |
| Acceptance Prediction| FR-7.1 - 7.3 | NFR-PERF-3, NFR-PRIV-2 | MLInferenceService / Scikit-learn / Joblib |
| Recommendation | FR-8.1 - 8.3 | NFR-PERF-3, NFR-USA-2 | RecommendationEngine / Scikit-learn |
| Demand Prediction | FR-9.1 - 9.3 | NFR-PERF-3, NFR-MAIN-3 | DemandPredictionService / Scikit-learn |
| Anomaly Detection | FR-10.1 - 10.2| NFR-PRIV-3, NFR-AVAIL-2| AnomalyDetectionService / Scikit-learn |
| Ratings & Reviews | FR-11.1 - 11.2| NFR-USA-3, NFR-REL-1 | RatingService / MySQL |
| Reports & Moderation| FR-12.1 - 12.2| NFR-SEC-2, NFR-PRIV-3 | ModerationService / Admin Portal |
| Notifications | FR-13.1 | NFR-USA-3, NFR-PERF-1 | NotificationService / Session Flashes |
| Admin Analytics | FR-14.1 - 14.3| NFR-SEC-4, NFR-AVAIL-2 | AdminService / Plotly / Seaborn |

# Database Design Specification: Smart Coupon Swap System

**Project Phase**: Phase 2 — Database Design & MySQL Implementation  
**Database Name**: `smart_coupon_swap`  
**RDBMS**: MySQL 8.x (InnoDB Engine)  
**Status**: Validated and Operational  

---

## 1. Database Purpose
The `smart_coupon_swap` database is a normalized relational database engine built on MySQL 8.x using the InnoDB storage engine. It provides ACID transaction guarantees, strict referential integrity, and behavioral interaction tracking for the Smart Coupon Swap System. 

The database serves two primary operational goals:
1. **Transactional Web Marketplace**: Powers day-to-day user registration, coupon cataloging, category/brand classification, bilateral swap negotiations, multi-party circular barter loops ($A \to B \to C \to A$), ratings, user moderation, and notification dispatches.
2. **Data Science & Machine Learning Foundation**: Accurately logs user-coupon behavioral telemetry (impressions, wishlist requests, redemption validations, savings metrics, and peer evaluations) to feed downstream feature engineering, recommendation algorithms, demand classifiers, and anomaly detectors.

---

## 2. Database Name & Technical Configuration
- **Database Name**: `smart_coupon_swap`
- **RDBMS Engine**: MySQL 8.x (InnoDB storage engine)
- **Character Set**: `utf8mb4` (complete Unicode and emoji support)
- **Collation**: `utf8mb4_unicode_ci` (case-insensitive standard Unicode sorting)
- **SQL Mode**: ANSI / STRICT_TRANS_TABLES compliant

---

## 3. Tables & Schema Inventory

The database consists of 17 normalized tables:

| Table Name | Functional Domain | Primary Key | Description |
| :--- | :--- | :--- | :--- |
| `roles` | Access Control | `role_id` | System authorization tiers (`ADMIN`, `USER`). |
| `users` | User Accounts | `user_id` | Profiles, authentication hashes, location, and reputation. |
| `categories` | Retail Taxonomy | `category_id` | Standardized coupon retail classifications. |
| `brands` | Merchant Registry | `brand_id` | E-commerce platforms and brand merchants. |
| `coupons` | Marketplace Assets | `coupon_id` | Coupon vouchers with monetary values in `DECIMAL(10, 2)`. |
| `user_category_preferences` | User Preferences | `(user_id, category_id)` | Normalized junction table for category affinities. |
| `user_brand_preferences` | User Preferences | `(user_id, brand_id)` | Normalized junction table for brand affinities. |
| `user_general_preferences` | User Preferences | `user_id` | Scalar trade preferences (min discount %, max expiry days). |
| `coupon_views` | Behavioral Telemetry | `view_id` | User and guest view impressions for demand forecasting. |
| `coupon_requests` | Interaction & Intent | `request_id` | Wishlist items and proactive swap interest expressions. |
| `coupon_usage` | Verification & Audit | `usage_id` | Post-swap redemption validation and realized savings logs. |
| `swaps` | Barter Transactions | `swap_id` | Master exchange proposals (bilateral and multi-user). |
| `swap_items` | Modular Transfer Legs | `swap_item_id` | Atomic voucher movements enabling circular chains ($A \to B \to C \to A$). |
| `swap_history` | Audit Ledger | `history_id` | Immutable state transition audit trail. |
| `ratings` | Trust & Reputation | `rating_id` | Post-swap bilateral peer evaluations (1 to 5 stars). |
| `reports` | Governance & Trust | `report_id` | Moderation tickets for abusive users, coupons, or swaps. |
| `notifications` | Communication | `notification_id` | In-app alerts for proposals, acceptances, and expiry warnings. |

---

## 4. Primary Keys
- **Surrogate Primary Keys**: Used across all independent entities (`roles`, `users`, `categories`, `brands`, `coupons`, `coupon_views`, `coupon_requests`, `coupon_usage`, `swaps`, `swap_items`, `swap_history`, `ratings`, `reports`, `notifications`) using `INT AUTO_INCREMENT` for high performance, deterministic indexing, and stable foreign-key references.
- **Natural Composite Primary Keys**: Used in junction tables:
  - `user_category_preferences`: `PRIMARY KEY (user_id, category_id)`
  - `user_brand_preferences`: `PRIMARY KEY (user_id, brand_id)`
- **One-to-One Primary Key**:
  - `user_general_preferences`: `PRIMARY KEY (user_id)` referencing `users(user_id)`.

---

## 5. Foreign Keys & Referential Actions

All foreign keys use explicit referential integrity rules:
- **`ON DELETE RESTRICT ON UPDATE CASCADE`**: Applied to protect critical transactional entities from accidental orphan deletion:
  - `users.role_id` $\to$ `roles.role_id`
  - `coupons.owner_id` $\to$ `users.user_id`
  - `coupons.category_id` $\to$ `categories.category_id`
  - `coupons.brand_id` $\to$ `brands.brand_id`
  - `swaps.initiator_id` / `swaps.receiver_id` $\to$ `users.user_id`
  - `swaps.offered_coupon_id` / `swaps.requested_coupon_id` $\to$ `coupons.coupon_id`
  - `coupon_usage.user_id` $\to$ `users.user_id`, `coupon_usage.coupon_id` $\to$ `coupons.coupon_id`
  - `reports.reporter_id` $\to$ `users.user_id`
- **`ON DELETE CASCADE ON UPDATE CASCADE`**: Applied where child rows strictly depend on the parent's lifecycle:
  - `user_category_preferences.user_id`, `user_brand_preferences.user_id`, `user_general_preferences.user_id` $\to$ `users.user_id`
  - `coupon_requests.requester_id` $\to$ `users.user_id`, `coupon_requests.coupon_id` $\to$ `coupons.coupon_id`
  - `swap_items.swap_id` $\to$ `swaps.swap_id`
  - `swap_history.swap_id` $\to$ `swaps.swap_id`
  - `ratings.swap_id` $\to$ `swaps.swap_id`
  - `notifications.user_id` $\to$ `users.user_id`
- **`ON DELETE RESTRICT ON UPDATE RESTRICT`**: Applied where columns participate in MySQL 8.0 `CHECK` constraints to satisfy engine constraints:
  - `swap_items.from_user_id`, `swap_items.to_user_id` $\to$ `users.user_id` (used in `chk_swapitems_users_different`)
  - `ratings.rater_id`, `ratings.rated_user_id` $\to$ `users.user_id` (used in `chk_ratings_no_self_rate`)
- **`ON DELETE SET NULL ON UPDATE CASCADE`**: Applied to optional relational links:
  - `brands.default_category_id` $\to$ `categories.category_id`
  - `coupon_views.user_id` $\to$ `users.user_id` (allows anonymous/guest browsing retention)
  - `swap_history.changed_by_user_id` $\to$ `users.user_id`

---

## 6. Important Relationships
- **Role-Based Authorization ($1 : M$)**: `roles` (1) $\to$ `users` (M) allows dynamic permission assignment.
- **Ownership ($1 : M$)**: `users` (1) $\to$ `coupons` (M) links listed vouchers to authenticated owners.
- **Taxonomy ($1 : M$)**: `categories` (1) $\to$ `coupons` (M) and `brands` (1) $\to$ `coupons` (M) standardize search filters.
- **User Taste Profiles ($M : M$)**: Normalized junction tables connect users to their preferred categories and brands.
- **Bilateral & Multi-User Barter ($1 : M$)**: `swaps` records the high-level trade; `swap_items` deconstructs the exchange into directed voucher transfer legs. This enables both direct bilateral swaps ($User_A \leftrightarrow User_B$) and circular cycles ($User_A \to User_B \to User_C \to User_A$).
- **Lifecycle Auditing ($1 : M$)**: `swaps` (1) $\to$ `swap_history` (M) tracks immutable state transitions.
- **Bilateral Feedback ($1 : M$)**: `swaps` (1) $\to$ `ratings` (M) ensures mutual evaluation.
- **Platform Moderation ($1 : M$)**: `users` (1) $\to$ `reports` (M) with polymorphic target classification (`COUPON`, `USER`, `SWAP`).

---

## 7. Normalization Decisions (3NF)
1. **First Normal Form (1NF)**: All attributes contain atomic scalar values. No multi-valued attributes or comma-separated lists exist in any table. User category and brand affinities are stored in dedicated junction tables.
2. **Second Normal Form (2NF)**: All non-key attributes are fully functionally dependent on the complete primary key. In composite primary key tables (`user_category_preferences`, `user_brand_preferences`), attributes like `preference_level` depend on both key components `(user_id, category_id)`.
3. **Third Normal Form (3NF)**: All transitive dependencies are removed:
   - Brand names, domains, and metadata are maintained in `brands`, referenced by `brand_id`.
   - Retail category metadata is maintained in `categories`, referenced by `category_id`.
   - Role names and descriptions are maintained in `roles`, referenced by `role_id`.
4. **Clean Moderation Design**: `reports` uses `(target_type, target_id)` rather than multiple nullable foreign key columns, eliminating sparse nullability and unnormalized columns.

---

## 8. Indexing Decisions

| Table | Index Name | Index Type | Columns | Query Optimization Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `users` | `idx_users_email` | UNIQUE | `email` | Sub-millisecond authentication lookups |
| `users` | `idx_users_role_id` | B-TREE | `role_id` | Role filtering and authorization queries |
| `users` | `idx_users_status` | B-TREE | `status` | Active user queries |
| `coupons` | `idx_coupons_marketplace` | COMPOSITE | `status, expiry_date, category_id` | Core marketplace search, category filtering, and expiry sorting |
| `coupons` | `idx_coupons_owner_id` | B-TREE | `owner_id` | User dashboard coupon portfolio retrieval |
| `coupons` | `idx_coupons_brand_id` | B-TREE | `brand_id` | Brand-specific deal listings |
| `coupon_views` | `idx_cviews_coupon_time` | COMPOSITE | `coupon_id, viewed_at` | Rapid aggregation of view velocity for demand prediction |
| `coupon_requests`| `uq_requester_coupon_status` | UNIQUE | `requester_id, coupon_id, status` | Prevents duplicate active requests |
| `swaps` | `idx_swaps_status` | B-TREE | `status` | Active negotiation filtering |
| `swaps` | `idx_swaps_proposed_at`| B-TREE | `proposed_at` | Timeline sorting for user ledgers |
| `swap_items` | `idx_swapitems_from_user` | B-TREE | `from_user_id` | Graph cycle traversal and user trade leg lookup |
| `swap_items` | `idx_swapitems_to_user` | B-TREE | `to_user_id` | Graph cycle traversal and user trade leg lookup |
| `ratings` | `uq_ratings_swap_rater` | UNIQUE | `swap_id, rater_id` | Guarantees one review per participant per swap |
| `reports` | `idx_reports_target` | COMPOSITE | `target_type, target_id` | Fast administrative moderation queue filtering |
| `notifications` | `idx_notifications_user_read` | COMPOSITE | `user_id, is_read` | Unread badge counts and inbox queries |

---

## 9. Constraints & Domain Integrity

- **Monetary Integrity**: All discount values, minimum purchase requirements, and savings calculations use `DECIMAL(10, 2)` (never `FLOAT` or `DOUBLE`) to prevent floating-point rounding errors.
- **Value Bounds**:
  - `chk_coupons_discount_positive`: `discount_value > 0`
  - `chk_coupons_min_purchase`: `min_purchase_amount >= 0`
  - `chk_coupons_dates`: `expiry_date >= issue_date`
  - `chk_users_reputation`: `reputation_score BETWEEN 0.00 AND 5.00`
  - `chk_ucp_pref_level`: `preference_level BETWEEN 1 AND 5`
  - `chk_ubp_pref_level`: `preference_level BETWEEN 1 AND 5`
  - `chk_ugp_discount`: `min_preferred_discount_pct BETWEEN 0 AND 100`
  - `chk_ugp_expiry_days`: `max_preferred_expiry_days > 0`
  - `chk_cusage_savings`: `savings_amount >= 0`
  - `chk_swaps_compatibility`: `compatibility_score IS NULL OR (compatibility_score >= 0.0000 AND compatibility_score <= 1.0000)`
  - `chk_swapitems_users_different`: `from_user_id <> to_user_id`
  - `chk_ratings_score`: `score BETWEEN 1 AND 5`
  - `chk_ratings_no_self_rate`: `rater_id <> rated_user_id`
- **Security & Masking**: Plaintext codes are not stored in the database. `coupon_code_encrypted` stores the ciphertext, remaining masked until mutual swap acceptance.

---

## 10. Future Data Science Usage
The schema provides structured historical event logging specifically designed to enable downstream exploratory data analysis and feature extraction:
1. **Behavioral Telemetry**: `coupon_views` captures timestamped impression events ($view\_count$, $view\_velocity$), enabling time-series analysis of brand and category popularity.
2. **Expressed Intent Signals**: `coupon_requests` records user interest, which serves as positive implicit feedback for collaborative filtering and preference matrix factorization.
3. **Outcome Auditing**: `coupon_usage` records actual redemption successes and failures, providing ground-truth labels for code validity prediction and savings verification.
4. **Reputation & Sentiment**: `ratings` provides numerical scores ($1-5$) and redemption confirmations, enabling user trust scoring and sentiment modeling.

---

## 11. Future Machine Learning Integration Considerations
The database schema directly supports the 4 machine learning components planned for later phases:
- **Coupon Acceptance Prediction**: Features can be extracted by joining `swaps`, `coupons`, and `user_category_preferences` (e.g., category match boolean, brand affinity score, relative value difference, days to expiry). The swap status (`ACCEPTED` vs `REJECTED`) serves as the binary target label.
- **Content-Based & Hybrid Recommendations**: The normalized `user_category_preferences` and `user_brand_preferences` tables provide structured numerical vectors to compute cosine similarity against coupon attribute vectors.
- **Coupon Demand Prediction**: `coupon_views`, `coupon_requests`, and `coupons` provide telemetry features (views per day, request-to-view ratio, discount depth) to train multiclass demand classifiers (`High`, `Medium`, `Low`).
- **Anomaly & Fraud Detection**: `coupon_views.ip_hash`, rapid insertion timestamps in `coupons`, and status transitions in `swap_history` allow unsupervised algorithms (Isolation Forest / LOF) to detect listing velocity anomalies and bot-like behavior.

-- ==============================================================================
-- SMART COUPON SWAP SYSTEM - DATABASE SCHEMA
-- ==============================================================================
-- Database Name: smart_coupon_swap
-- Target RDBMS: MySQL 8.x
-- Compatibility: MySQL Workbench 8.x & MySQL Shell / CLI
-- Storage Engine: InnoDB
-- Character Set: utf8mb4
-- Collation: utf8mb4_unicode_ci
-- Normalization Level: Third Normal Form (3NF)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- DATABASE INITIALIZATION
-- ------------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS smart_coupon_swap
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE smart_coupon_swap;

-- ------------------------------------------------------------------------------
-- 1. ROLES TABLE
-- ------------------------------------------------------------------------------
-- Supports Role-Based Access Control (RBAC).
-- Standard roles: 'ADMIN', 'USER'
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. USERS TABLE
-- ------------------------------------------------------------------------------
-- User account profiles, demographic information, and reputation scoring.
-- NEVER stores plaintext passwords; stores cryptographic hash placeholder (bcrypt/Argon2).
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NULL,
    city VARCHAR(100) NULL,
    state VARCHAR(100) NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    status ENUM('ACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION', 'DEACTIVATED') NOT NULL DEFAULT 'ACTIVE',
    reputation_score DECIMAL(3, 2) NOT NULL DEFAULT 5.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) 
        REFERENCES roles(role_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_users_reputation CHECK (reputation_score >= 0.00 AND reputation_score <= 5.00)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_city ON users(city);

-- ------------------------------------------------------------------------------
-- 3. CATEGORIES TABLE
-- ------------------------------------------------------------------------------
-- Standardized retail taxonomy for coupon classification.
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. BRANDS TABLE
-- ------------------------------------------------------------------------------
-- Stores retail merchants, platforms, and brands offering vouchers.
CREATE TABLE IF NOT EXISTS brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    default_category_id INT NULL,
    website_url VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_brands_default_category FOREIGN KEY (default_category_id)
        REFERENCES categories(category_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_brands_default_category ON brands(default_category_id);

-- ------------------------------------------------------------------------------
-- 5. COUPONS TABLE
-- ------------------------------------------------------------------------------
-- Central coupon repository listed by users. Monetary values use DECIMAL(10, 2).
-- Plaintext voucher codes are never stored directly; coupon_code_encrypted holds ciphertext.
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    coupon_code_encrypted VARCHAR(255) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    discount_type ENUM('PERCENTAGE', 'FLAT_AMOUNT', 'CASHBACK', 'BUY_ONE_GET_ONE', 'OTHER') NOT NULL DEFAULT 'PERCENTAGE',
    discount_value DECIMAL(10, 2) NOT NULL,
    min_purchase_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    max_discount_amount DECIMAL(10, 2) NULL,
    terms_and_conditions TEXT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status ENUM('ACTIVE', 'EXPIRED', 'REDEEMED', 'SWAPPED', 'REMOVED') NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_coupons_owner FOREIGN KEY (owner_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_coupons_category FOREIGN KEY (category_id)
        REFERENCES categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_coupons_brand FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_coupons_discount_positive CHECK (discount_value > 0),
    CONSTRAINT chk_coupons_min_purchase CHECK (min_purchase_amount >= 0),
    CONSTRAINT chk_coupons_dates CHECK (expiry_date >= issue_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_coupons_owner_id ON coupons(owner_id);
CREATE INDEX idx_coupons_category_id ON coupons(category_id);
CREATE INDEX idx_coupons_brand_id ON coupons(brand_id);
CREATE INDEX idx_coupons_status ON coupons(status);
CREATE INDEX idx_coupons_expiry_date ON coupons(expiry_date);
CREATE INDEX idx_coupons_marketplace ON coupons(status, expiry_date, category_id);

-- ------------------------------------------------------------------------------
-- 6. USER PREFERENCES (3NF NORMALIZED JUNCTION TABLES)
-- ------------------------------------------------------------------------------
-- Junction table: User preferred categories (avoids comma-separated values)
CREATE TABLE IF NOT EXISTS user_category_preferences (
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    preference_level TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, category_id),
    CONSTRAINT fk_ucp_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ucp_category FOREIGN KEY (category_id)
        REFERENCES categories(category_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_ucp_pref_level CHECK (preference_level BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_ucp_category_id ON user_category_preferences(category_id);

-- Junction table: User preferred brands (avoids comma-separated values)
CREATE TABLE IF NOT EXISTS user_brand_preferences (
    user_id INT NOT NULL,
    brand_id INT NOT NULL,
    preference_level TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, brand_id),
    CONSTRAINT fk_ubp_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ubp_brand FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_ubp_pref_level CHECK (preference_level BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_ubp_brand_id ON user_brand_preferences(brand_id);

-- General user barter preferences (min discount, max expiry horizon)
CREATE TABLE IF NOT EXISTS user_general_preferences (
    user_id INT PRIMARY KEY,
    min_preferred_discount_pct DECIMAL(5, 2) NULL DEFAULT 10.00,
    max_preferred_expiry_days INT NULL DEFAULT 30,
    preferred_location VARCHAR(100) NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_ugp_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_ugp_discount CHECK (min_preferred_discount_pct >= 0 AND min_preferred_discount_pct <= 100),
    CONSTRAINT chk_ugp_expiry_days CHECK (max_preferred_expiry_days > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 7. COUPON VIEWS TABLE
-- ------------------------------------------------------------------------------
-- Captures user and guest browsing telemetry for recommendation and demand modeling.
-- user_id is nullable to capture anonymous guest impressions.
CREATE TABLE IF NOT EXISTS coupon_views (
    view_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    coupon_id INT NOT NULL,
    viewed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_hash VARCHAR(64) NULL,
    session_id VARCHAR(100) NULL,
    CONSTRAINT fk_cviews_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_cviews_coupon FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_cviews_coupon_id ON coupon_views(coupon_id);
CREATE INDEX idx_cviews_user_id ON coupon_views(user_id);
CREATE INDEX idx_cviews_coupon_time ON coupon_views(coupon_id, viewed_at);

-- ------------------------------------------------------------------------------
-- 8. COUPON REQUESTS TABLE
-- ------------------------------------------------------------------------------
-- Tracks users expressing active interest or wishlist requests for a coupon.
-- Unique constraint prevents redundant active requests with identical status.
CREATE TABLE IF NOT EXISTS coupon_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    requester_id INT NOT NULL,
    coupon_id INT NOT NULL,
    status ENUM('PENDING', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'EXPIRED') NOT NULL DEFAULT 'PENDING',
    message VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_crequests_requester FOREIGN KEY (requester_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_crequests_coupon FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_requester_coupon_status UNIQUE (requester_id, coupon_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_crequests_coupon_status ON coupon_requests(coupon_id, status);
CREATE INDEX idx_crequests_requester ON coupon_requests(requester_id);

-- ------------------------------------------------------------------------------
-- 9. COUPON USAGE TABLE
-- ------------------------------------------------------------------------------
-- Records coupon redemption results, monetary savings, and code validity feedback.
CREATE TABLE IF NOT EXISTS coupon_usage (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    redemption_status ENUM('SUCCESS', 'FAILED_INVALID_CODE', 'FAILED_EXPIRED', 'FAILED_MIN_PURCHASE', 'OTHER') NOT NULL DEFAULT 'SUCCESS',
    savings_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    feedback_notes VARCHAR(255) NULL,
    CONSTRAINT fk_cusage_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_cusage_coupon FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_cusage_savings CHECK (savings_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_cusage_user ON coupon_usage(user_id);
CREATE INDEX idx_cusage_coupon ON coupon_usage(coupon_id);
CREATE INDEX idx_cusage_status ON coupon_usage(redemption_status);

-- ------------------------------------------------------------------------------
-- 10. SWAPS TABLE
-- ------------------------------------------------------------------------------
-- Represents bilateral or multi-user barter transactions.
-- compatibility_score is a DECIMAL(5, 4) placeholder (0.0000 to 1.0000) for future ML score.
CREATE TABLE IF NOT EXISTS swaps (
    swap_id INT AUTO_INCREMENT PRIMARY KEY,
    swap_type ENUM('BILATERAL', 'MULTI_USER') NOT NULL DEFAULT 'BILATERAL',
    initiator_id INT NOT NULL,
    receiver_id INT NULL,
    offered_coupon_id INT NULL,
    requested_coupon_id INT NULL,
    compatibility_score DECIMAL(5, 4) NULL,
    status ENUM('PROPOSED', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED', 'FAILED') NOT NULL DEFAULT 'PROPOSED',
    proposed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    CONSTRAINT fk_swaps_initiator FOREIGN KEY (initiator_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_swaps_receiver FOREIGN KEY (receiver_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_swaps_offered_coupon FOREIGN KEY (offered_coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_swaps_requested_coupon FOREIGN KEY (requested_coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_swaps_compatibility CHECK (compatibility_score IS NULL OR (compatibility_score >= 0.0000 AND compatibility_score <= 1.0000))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_swaps_initiator ON swaps(initiator_id);
CREATE INDEX idx_swaps_receiver ON swaps(receiver_id);
CREATE INDEX idx_swaps_status ON swaps(status);
CREATE INDEX idx_swaps_proposed_at ON swaps(proposed_at);

-- ------------------------------------------------------------------------------
-- 11. SWAP ITEMS TABLE (MODULAR / MULTI-USER SWAP LEGS)
-- ------------------------------------------------------------------------------
-- Deconstructs swaps into atomic transfer legs.
-- Directly supports both standard bilateral swaps and 3-way circular barter chains (A -> B -> C -> A).
CREATE TABLE IF NOT EXISTS swap_items (
    swap_item_id INT AUTO_INCREMENT PRIMARY KEY,
    swap_id INT NOT NULL,
    from_user_id INT NOT NULL,
    to_user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    status ENUM('PENDING', 'CONFIRMED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_swapitems_swap FOREIGN KEY (swap_id)
        REFERENCES swaps(swap_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_swapitems_from_user FOREIGN KEY (from_user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_swapitems_to_user FOREIGN KEY (to_user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_swapitems_coupon FOREIGN KEY (coupon_id)
        REFERENCES coupons(coupon_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_swapitems_users_different CHECK (from_user_id <> to_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_swapitems_swap_id ON swap_items(swap_id);
CREATE INDEX idx_swapitems_from_user ON swap_items(from_user_id);
CREATE INDEX idx_swapitems_to_user ON swap_items(to_user_id);
CREATE INDEX idx_swapitems_coupon ON swap_items(coupon_id);

-- ------------------------------------------------------------------------------
-- 12. SWAP HISTORY TABLE
-- ------------------------------------------------------------------------------
-- Immutable state transition audit ledger tracking every lifecycle event of a swap.
CREATE TABLE IF NOT EXISTS swap_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    swap_id INT NOT NULL,
    previous_status ENUM('PROPOSED', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED', 'FAILED') NULL,
    new_status ENUM('PROPOSED', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED', 'FAILED') NOT NULL,
    changed_by_user_id INT NULL,
    notes VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_swaphistory_swap FOREIGN KEY (swap_id)
        REFERENCES swaps(swap_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_swaphistory_user FOREIGN KEY (changed_by_user_id)
        REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_swaphistory_swap_id ON swap_history(swap_id);
CREATE INDEX idx_swaphistory_created ON swap_history(created_at);

-- ------------------------------------------------------------------------------
-- 13. RATINGS TABLE
-- ------------------------------------------------------------------------------
-- Bilateral peer evaluations submitted upon swap completion.
-- Unique constraint enforces one rating per rater per swap; check constraint prevents self-ratings.
CREATE TABLE IF NOT EXISTS ratings (
    rating_id INT AUTO_INCREMENT PRIMARY KEY,
    swap_id INT NOT NULL,
    rater_id INT NOT NULL,
    rated_user_id INT NOT NULL,
    score TINYINT NOT NULL,
    review_text TEXT NULL,
    code_worked BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ratings_swap FOREIGN KEY (swap_id)
        REFERENCES swaps(swap_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ratings_rater FOREIGN KEY (rater_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_ratings_rated_user FOREIGN KEY (rated_user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT uq_ratings_swap_rater UNIQUE (swap_id, rater_id),
    CONSTRAINT chk_ratings_score CHECK (score BETWEEN 1 AND 5),
    CONSTRAINT chk_ratings_no_self_rate CHECK (rater_id <> rated_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_ratings_rated_user ON ratings(rated_user_id);
CREATE INDEX idx_ratings_rater ON ratings(rater_id);

-- ------------------------------------------------------------------------------
-- 14. REPORTS TABLE
-- ------------------------------------------------------------------------------
-- Moderation tickets submitted by users to report abusive accounts, invalid coupons, or swaps.
CREATE TABLE IF NOT EXISTS reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT NOT NULL,
    target_type ENUM('COUPON', 'USER', 'SWAP') NOT NULL,
    target_id INT NOT NULL,
    reason VARCHAR(100) NOT NULL,
    description TEXT NULL,
    status ENUM('OPEN', 'REVIEWING', 'RESOLVED', 'REJECTED') NOT NULL DEFAULT 'OPEN',
    admin_notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    CONSTRAINT fk_reports_reporter FOREIGN KEY (reporter_id)
        REFERENCES users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_reporter ON reports(reporter_id);
CREATE INDEX idx_reports_target ON reports(target_type, target_id);
CREATE INDEX idx_reports_created ON reports(created_at);

-- ------------------------------------------------------------------------------
-- 15. NOTIFICATIONS TABLE
-- ------------------------------------------------------------------------------
-- User in-app notifications for swap proposals, acceptances, rejections, and alerts.
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('SWAP_PROPOSAL', 'SWAP_ACCEPTED', 'SWAP_REJECTED', 'SWAP_COMPLETED', 'COUPON_EXPIRING', 'SMART_MATCH_FOUND', 'SYSTEM_ALERT') NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    reference_id INT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

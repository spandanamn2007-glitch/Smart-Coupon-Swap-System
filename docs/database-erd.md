# Database Entity-Relationship Diagram (ERD)

**Project**: Smart Coupon Swap System  
**Phase**: Phase 2 — Database Design & MySQL Implementation  
**Database**: `smart_coupon_swap`  
**RDBMS**: MySQL 8.x (InnoDB Engine)  

The following Mermaid Entity-Relationship diagram accurately represents the physical schema implemented in [`database/schema.sql`](file:///C:/Users/chand/.gemini/antigravity/scratch/smart-coupon-swap-system/database/schema.sql).

---

```mermaid
erDiagram
    roles ||--o{ users : "assigned_to"
    categories ||--o{ brands : "categorizes"
    categories ||--o{ coupons : "classifies"
    brands ||--o{ coupons : "issued_by"
    users ||--o{ coupons : "owns"

    users ||--o{ user_category_preferences : "specifies"
    categories ||--o{ user_category_preferences : "preferred_category"

    users ||--o{ user_brand_preferences : "specifies"
    brands ||--o{ user_brand_preferences : "preferred_brand"

    users ||--|| user_general_preferences : "configures"

    users ||--o{ coupon_views : "views"
    coupons ||--o{ coupon_views : "viewed_in"

    users ||--o{ coupon_requests : "submits_request"
    coupons ||--o{ coupon_requests : "targeted_by"

    users ||--o{ coupon_usage : "redeems"
    coupons ||--o{ coupon_usage : "redeemed_in"

    users ||--o{ swaps : "initiates"
    users ||--o{ swaps : "receives"
    coupons ||--o{ swaps : "offers"
    coupons ||--o{ swaps : "requests"

    swaps ||--|{ swap_items : "contains_legs"
    users ||--o{ swap_items : "from_user"
    users ||--o{ swap_items : "to_user"
    coupons ||--o{ swap_items : "transfers"

    swaps ||--o{ swap_history : "audited_by"
    users ||--o{ swap_history : "transitioned_by"

    swaps ||--o{ ratings : "evaluated_in"
    users ||--o{ ratings : "submits"
    users ||--o{ ratings : "receives_rating"

    users ||--o{ reports : "submits_report"
    users ||--o{ notifications : "receives"

    roles {
        int role_id PK
        string role_name UK
        string description
        timestamp created_at
    }

    users {
        int user_id PK
        int role_id FK
        string name
        string email UK
        string password_hash
        string phone
        string city
        string state
        string country
        string status
        decimal reputation_score
        timestamp created_at
        timestamp updated_at
    }

    categories {
        int category_id PK
        string name UK
        string slug UK
        string description
        timestamp created_at
    }

    brands {
        int brand_id PK
        string name UK
        int default_category_id FK
        string website_url
        timestamp created_at
    }

    coupons {
        int coupon_id PK
        int owner_id FK
        int category_id FK
        int brand_id FK
        string coupon_code_encrypted
        string title
        text description
        string discount_type
        decimal discount_value
        decimal min_purchase_amount
        decimal max_discount_amount
        text terms_and_conditions
        date issue_date
        date expiry_date
        string status
        timestamp created_at
        timestamp updated_at
    }

    user_category_preferences {
        int user_id PK, FK
        int category_id PK, FK
        tinyint preference_level
        timestamp created_at
    }

    user_brand_preferences {
        int user_id PK, FK
        int brand_id PK, FK
        tinyint preference_level
        timestamp created_at
    }

    user_general_preferences {
        int user_id PK, FK
        decimal min_preferred_discount_pct
        int max_preferred_expiry_days
        string preferred_location
        timestamp updated_at
    }

    coupon_views {
        int view_id PK
        int user_id FK
        int coupon_id FK
        timestamp viewed_at
        string ip_hash
        string session_id
    }

    coupon_requests {
        int request_id PK
        int requester_id FK
        int coupon_id FK
        string status
        string message
        timestamp created_at
        timestamp updated_at
    }

    coupon_usage {
        int usage_id PK
        int user_id FK
        int coupon_id FK
        timestamp used_at
        string redemption_status
        decimal savings_amount
        string feedback_notes
    }

    swaps {
        int swap_id PK
        string swap_type
        int initiator_id FK
        int receiver_id FK
        int offered_coupon_id FK
        int requested_coupon_id FK
        decimal compatibility_score
        string status
        timestamp proposed_at
        timestamp completed_at
    }

    swap_items {
        int swap_item_id PK
        int swap_id FK
        int from_user_id FK
        int to_user_id FK
        int coupon_id FK
        string status
        timestamp created_at
    }

    swap_history {
        int history_id PK
        int swap_id FK
        string previous_status
        string new_status
        int changed_by_user_id FK
        string notes
        timestamp created_at
    }

    ratings {
        int rating_id PK
        int swap_id FK
        int rater_id FK
        int rated_user_id FK
        tinyint score
        text review_text
        boolean code_worked
        timestamp created_at
    }

    reports {
        int report_id PK
        int reporter_id FK
        string target_type
        int target_id
        string reason
        text description
        string status
        text admin_notes
        timestamp created_at
        timestamp resolved_at
    }

    notifications {
        int notification_id PK
        int user_id FK
        string type
        string title
        text message
        int reference_id
        boolean is_read
        timestamp created_at
    }
```

---

## Entity Relationship Overview
- **Roles (1) to Users (M)**: System authorization tier enforcing permissions for administrators and standard users.
- **Users (1) to Coupons (M)**: Ownership relationship tracking who created and holds the voucher.
- **Categories (1) to Coupons (M)**: Retail taxonomy classification.
- **Brands (1) to Coupons (M)**: Merchant and platform affiliation.
- **Users (M) to Categories (M)**: Many-to-many relationship normalized via `user_category_preferences`.
- **Users (M) to Brands (M)**: Many-to-many relationship normalized via `user_brand_preferences`.
- **Users (1) to General Preferences (1)**: Single scalar preferences row per user storing trading thresholds.
- **Coupons (1) to Views (M)**: Behavioral impression tracking for popularity and demand modeling.
- **Coupons (1) to Requests (M)**: Wishlist and swap intent signals.
- **Coupons (1) to Usage (M)**: Post-exchange redemption verification and savings auditing.
- **Users (M) to Swaps (M)**: Master barter agreements for bilateral and multi-user exchanges.
- **Swaps (1) to Swap Items (M)**: Transfer legs deconstructing trades into atomic voucher movements (enabling 3-way circular loops: $A \to B \to C \to A$).
- **Swaps (1) to History (M)**: Immutable state transition audit trail (`PROPOSED` $\to$ `ACCEPTED` $\to$ `COMPLETED`).
- **Swaps (1) to Ratings (M)**: Bilateral peer trust evaluations with anti-self-rating constraints.
- **Users (1) to Reports (M)**: Moderation tickets for reporting users, coupons, or transactions.
- **Users (1) to Notifications (M)**: User communication alerts for transaction events.

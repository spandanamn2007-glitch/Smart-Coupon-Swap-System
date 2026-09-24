-- ==============================================================================
-- SMART COUPON SWAP SYSTEM - MINIMAL SEED REFERENCE DATA
-- ==============================================================================
-- Database: smart_coupon_swap
-- Purpose: Reference taxonomy and verification seed data for Phase 2 validation.
-- Note: Large-scale synthetic datasets for ML will be generated in Phase 3.
-- ==============================================================================

USE smart_coupon_swap;

-- ------------------------------------------------------------------------------
-- 1. SEED ROLES
-- ------------------------------------------------------------------------------
INSERT INTO roles (role_id, role_name, description) VALUES
(1, 'ADMIN', 'System administrator with platform governance and moderation privileges'),
(2, 'USER', 'Standard registered platform user capable of listing and swapping coupons')
ON DUPLICATE KEY UPDATE 
    role_name = VALUES(role_name),
    description = VALUES(description);

-- ------------------------------------------------------------------------------
-- 2. SEED CATEGORIES
-- ------------------------------------------------------------------------------
INSERT INTO categories (category_id, name, slug, description) VALUES
(1, 'Food & Dining', 'food-dining', 'Restaurants, cafes, food delivery, and beverage discounts'),
(2, 'Fashion & Apparel', 'fashion-apparel', 'Clothing, footwear, accessories, and designer wear'),
(3, 'Electronics & Gadgets', 'electronics-gadgets', 'Smartphones, laptops, accessories, and home appliances'),
(4, 'Travel & Hospitality', 'travel-hospitality', 'Flights, hotels, holiday packages, and cab services'),
(5, 'Entertainment & Streaming', 'entertainment-streaming', 'Cinema tickets, OTT subscriptions, concerts, and gaming'),
(6, 'Grocery & Essentials', 'grocery-essentials', 'Supermarkets, daily essentials, and quick-commerce groceries'),
(7, 'Health & Beauty', 'health-beauty', 'Skincare, cosmetics, wellness, and pharmaceutical discounts'),
(8, 'Other', 'other', 'Miscellaneous vouchers and multi-category promotional deals')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    slug = VALUES(slug),
    description = VALUES(description);

-- ------------------------------------------------------------------------------
-- 3. SEED BRANDS
-- ------------------------------------------------------------------------------
INSERT INTO brands (brand_id, name, default_category_id, website_url) VALUES
(1, 'Amazon', 3, 'https://www.amazon.in'),
(2, 'Flipkart', 3, 'https://www.flipkart.com'),
(3, 'Myntra', 2, 'https://www.myntra.com'),
(4, 'Ajio', 2, 'https://www.ajio.com'),
(5, 'Swiggy', 1, 'https://www.swiggy.com'),
(6, 'Zomato', 1, 'https://www.zomato.com'),
(7, 'Uber', 4, 'https://www.uber.com'),
(8, 'MakeMyTrip', 4, 'https://www.makemytrip.com'),
(9, 'BookMyShow', 5, 'https://in.bookmyshow.com'),
(10, 'Blinkit', 6, 'https://www.blinkit.com'),
(11, 'PUMA', 2, 'https://in.puma.com')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    default_category_id = VALUES(default_category_id),
    website_url = VALUES(website_url);

-- ------------------------------------------------------------------------------
-- 4. VERIFICATION SAMPLE USERS (FOR SCHEMA VALIDATION ONLY)
-- ------------------------------------------------------------------------------
-- Passwords are non-plaintext dummy hash placeholders for development testing.
INSERT INTO users (user_id, role_id, name, email, password_hash, phone, city, state, country, status) VALUES
(1, 1, 'Admin Moderator', 'admin@smartswap.local', '$2b$12$DUMMY_HASH_PLACEHOLDER_FOR_SCHEMA_VERIFICATION_001', '9876543210', 'Bengaluru', 'Karnataka', 'India', 'ACTIVE'),
(2, 2, 'Demo Swapper A', 'user.a@smartswap.local', '$2b$12$DUMMY_HASH_PLACEHOLDER_FOR_SCHEMA_VERIFICATION_002', '9876543211', 'Mumbai', 'Maharashtra', 'India', 'ACTIVE'),
(3, 2, 'Demo Swapper B', 'user.b@smartswap.local', '$2b$12$DUMMY_HASH_PLACEHOLDER_FOR_SCHEMA_VERIFICATION_003', '9876543212', 'Delhi', 'Delhi', 'India', 'ACTIVE')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    email = VALUES(email);

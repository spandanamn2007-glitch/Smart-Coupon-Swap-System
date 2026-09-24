"""
Recommendation Service
Smart Coupon Swap System

Provides explainable rule-based and content-filtering recommendations for authenticated users.
Uses exact Phase 2 database/schema.sql column definitions.
"""

from app.services.db import execute_one, execute_all


def get_recommendations_for_user(user_id, limit=10):
    """Computes explainable coupon recommendations for a user."""
    prefs = execute_one(
        "SELECT min_preferred_discount_pct, max_preferred_expiry_days, preferred_location FROM user_general_preferences WHERE user_id = %s;",
        (user_id,)
    ) or {}

    min_disc = prefs.get("min_preferred_discount_pct") or 10.0
    location = prefs.get("preferred_location")

    cat_prefs = execute_all("SELECT category_id FROM user_category_preferences WHERE user_id = %s;", (user_id,))
    pref_cat_ids = [c["category_id"] for c in cat_prefs]

    brand_prefs = execute_all("SELECT brand_id FROM user_brand_preferences WHERE user_id = %s;", (user_id,))
    pref_brand_ids = [b["brand_id"] for b in brand_prefs]

    sql = """
        SELECT c.*, cat.name AS category_name, b.name AS brand_name, u.name AS owner_name
        FROM coupons c
        JOIN categories cat ON c.category_id = cat.category_id
        JOIN brands b ON c.brand_id = b.brand_id
        JOIN users u ON c.owner_id = u.user_id
        WHERE c.status = 'ACTIVE'
          AND c.expiry_date >= CURRENT_DATE()
          AND c.owner_id != %s
        ORDER BY c.coupon_id DESC
        LIMIT 200;
    """
    candidates = execute_all(sql, (user_id,))

    scored_recommendations = []
    for c in candidates:
        score = 0
        reasons = []

        if pref_cat_ids and c["category_id"] in pref_cat_ids:
            score += 40
            reasons.append(f"Matches your saved preferred category: {c['category_name']}")
        
        if pref_brand_ids and c["brand_id"] in pref_brand_ids:
            score += 35
            reasons.append(f"Matches your saved preferred brand: {c['brand_name']}")

        if float(c["discount_value"]) >= float(min_disc):
            score += 20
            reasons.append(f"Meets your minimum discount threshold ({min_disc}%)")

        u_city = c.get("city")
        if location and u_city and u_city.lower() == location.lower():
            score += 15
            reasons.append(f"Available in your preferred city: {u_city}")

        if not reasons:
            score += 10
            reasons.append(f"Popular listing in {c['category_name']}")

        scored_recommendations.append({
            "coupon": c,
            "recommendation_score": score,
            "explanation": " | ".join(reasons)
        })

    scored_recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return scored_recommendations[:limit]

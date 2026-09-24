"""
Smart 2-Way Swap Compatibility Service
Smart Coupon Swap System

Computes explainable bilateral swap compatibility scores (0.0 - 100.0).
Validates coupon availability, expiration status, and ownership boundaries.
"""

from datetime import datetime
from app.services.coupon_service import get_coupon_by_id


def calculate_swap_compatibility(offered_coupon_id, requested_coupon_id):
    """Calculates explainable bilateral swap compatibility score."""
    c_offered = get_coupon_by_id(offered_coupon_id)
    c_requested = get_coupon_by_id(requested_coupon_id)

    # 1. Validation checks
    if not c_offered:
        return None, "Offered coupon not found"
    if not c_requested:
        return None, "Requested coupon not found"

    if c_offered["owner_id"] == c_requested["owner_id"]:
        return None, "Invalid Swap: Cannot swap coupons owned by the same user"

    if c_offered["status"] != "ACTIVE" or c_requested["status"] != "ACTIVE":
        return None, "Invalid Swap: One or both coupons are not currently available"

    today_str = datetime.today().strftime("%Y-%m-%d")
    if str(c_offered["expiry_date"]) < today_str or str(c_requested["expiry_date"]) < today_str:
        return None, "Invalid Swap: One or both coupons have expired"

    # 2. Score Calculation Components
    breakdown = {}

    # Component A: Monetary Value Parity (max 35 pts)
    val_a = float(c_offered["discount_value"])
    val_b = float(c_requested["discount_value"])
    ratio = min(val_a, val_b) / max(val_a, val_b)
    value_score = round(ratio * 35.0, 2)
    breakdown["value_parity_score"] = value_score
    breakdown["value_ratio"] = round(val_a / (val_b + 1e-5), 3)

    # Component B: Category Match (max 25 pts)
    cat_match = c_offered["category_id"] == c_requested["category_id"]
    cat_score = 25.0 if cat_match else 10.0
    breakdown["category_match_score"] = cat_score
    breakdown["same_category"] = cat_match

    # Component C: Brand Match (max 20 pts)
    brand_match = c_offered["brand_id"] == c_requested["brand_id"]
    brand_score = 20.0 if brand_match else 5.0
    breakdown["brand_match_score"] = brand_score
    breakdown["same_brand"] = brand_match

    # Component D: Validity Window Alignment (max 20 pts)
    exp_a = datetime.strptime(str(c_offered["expiry_date"]), "%Y-%m-%d")
    exp_b = datetime.strptime(str(c_requested["expiry_date"]), "%Y-%m-%d")
    days_diff = abs((exp_a - exp_b).days)
    validity_score = max(0.0, round(20.0 - (days_diff / 15.0), 2))
    breakdown["validity_alignment_score"] = validity_score
    breakdown["expiry_days_difference"] = days_diff

    total_score = round(value_score + cat_score + brand_score + validity_score, 2)

    return {
        "compatibility_score": total_score,
        "is_compatible": total_score >= 50.0,
        "score_breakdown": breakdown,
        "offered_coupon": {
            "coupon_id": c_offered["coupon_id"],
            "title": c_offered["title"],
            "value": val_a,
            "owner_id": c_offered["owner_id"]
        },
        "requested_coupon": {
            "coupon_id": c_requested["coupon_id"],
            "title": c_requested["title"],
            "value": val_b,
            "owner_id": c_requested["owner_id"]
        }
    }, None

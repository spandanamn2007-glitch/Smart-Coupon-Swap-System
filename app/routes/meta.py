"""
Metadata Routes — Categories & Brands
Smart Coupon Swap System

Serves canonical taxonomy data (categories, brands) for UI dropdowns.
These are read-only, publicly accessible endpoints because they contain
no sensitive information and are needed to populate Add Coupon forms.
"""

from flask import Blueprint, jsonify, request
from app.services.db import execute_all

meta_bp = Blueprint("meta", __name__, url_prefix="/api/meta")


@meta_bp.route("/categories", methods=["GET"])
def list_categories():
    """Return all categories ordered by name."""
    rows = execute_all(
        "SELECT category_id, name, slug FROM categories ORDER BY name ASC;"
    )
    # Ensure int IDs for JSON
    for r in rows:
        r["category_id"] = int(r["category_id"])
    return jsonify({"categories": rows}), 200


@meta_bp.route("/brands", methods=["GET"])
def list_brands():
    """Return brands, optionally filtered by category_id query param."""
    category_id = request.args.get("category_id")
    if category_id:
        rows = execute_all(
            "SELECT brand_id, name, default_category_id FROM brands "
            "WHERE default_category_id = %s ORDER BY name ASC;",
            (int(category_id),)
        )
    else:
        rows = execute_all(
            "SELECT brand_id, name, default_category_id FROM brands ORDER BY name ASC;"
        )
    for r in rows:
        r["brand_id"] = int(r["brand_id"])
        r["default_category_id"] = int(r["default_category_id"]) if r.get("default_category_id") else None
    return jsonify({"brands": rows}), 200

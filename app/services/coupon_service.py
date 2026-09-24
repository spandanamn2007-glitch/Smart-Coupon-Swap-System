"""
Coupon Marketplace Service
Smart Coupon Swap System

Handles CRUD operations, ownership verification, search, filtering, and status checks.
Uses exact Phase 2 database/schema.sql column definitions.
"""

from datetime import datetime
from app.services.db import execute_one, execute_all, execute_write


def get_coupon_by_id(coupon_id):
    """Retrieves a single coupon record by ID with category and brand details."""
    sql = """
        SELECT c.*, cat.name AS category_name, b.name AS brand_name, u.name AS owner_name, u.email AS owner_email
        FROM coupons c
        JOIN categories cat ON c.category_id = cat.category_id
        JOIN brands b ON c.brand_id = b.brand_id
        JOIN users u ON c.owner_id = u.user_id
        WHERE c.coupon_id = %s;
    """
    return execute_one(sql, (coupon_id,))


def create_coupon(owner_id, data):
    """Creates a new coupon record for the authenticated user."""
    category_id = int(data.get("category_id", 1))
    brand_id = int(data.get("brand_id", 1))
    discount_type = data.get("discount_type", "PERCENTAGE").upper()
    if discount_type not in ["PERCENTAGE", "FLAT_AMOUNT", "CASHBACK", "BUY_ONE_GET_ONE", "OTHER"]:
        discount_type = "PERCENTAGE"

    discount_value = float(data.get("discount_value", 10.0))
    min_purchase_amount = float(data.get("min_purchase_amount", data.get("minimum_purchase", 0.0)))
    issue_date = data.get("issue_date", datetime.today().strftime("%Y-%m-%d"))
    expiry_date = data.get("expiry_date")
    title = data.get("title", "Promotional Voucher").strip()
    description = data.get("description", "").strip() or None
    coupon_code = data.get("coupon_code", "SAVE" + str(datetime.now().microsecond)).strip()

    if not expiry_date:
        raise ValueError("Expiry date is required")

    if discount_value <= 0:
        raise ValueError("Discount value must be strictly positive")

    if datetime.strptime(expiry_date, "%Y-%m-%d") < datetime.strptime(issue_date, "%Y-%m-%d"):
        raise ValueError("Expiry date cannot be prior to issue date")

    sql = """
        INSERT INTO coupons (
            owner_id, category_id, brand_id, coupon_code_encrypted, title,
            description, discount_type, discount_value, min_purchase_amount,
            issue_date, expiry_date, status
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, 'ACTIVE'
        );
    """
    params = (
        owner_id, category_id, brand_id, coupon_code, title,
        description, discount_type, discount_value, min_purchase_amount,
        issue_date, expiry_date
    )
    coupon_id, _ = execute_write(sql, params)
    return get_coupon_by_id(coupon_id)


def update_coupon(coupon_id, owner_id, data):
    """Updates an existing coupon, enforcing ownership boundary."""
    existing = get_coupon_by_id(coupon_id)
    if not existing:
        return None, "Coupon not found"
    if int(existing["owner_id"]) != int(owner_id):
        return None, "Forbidden: You do not own this coupon"

    fields = []
    params = []
    if "title" in data and data["title"]:
        fields.append("title = %s")
        params.append(data["title"].strip())
    if "description" in data:
        fields.append("description = %s")
        params.append(data["description"].strip() if data["description"] else None)
    if "discount_value" in data and data["discount_value"] is not None:
        fields.append("discount_value = %s")
        params.append(float(data["discount_value"]))
    if "status" in data and data["status"]:
        fields.append("status = %s")
        params.append(data["status"].upper())

    if not fields:
        return existing, "No valid fields provided for update"

    params.append(coupon_id)
    update_sql = f"UPDATE coupons SET {', '.join(fields)} WHERE coupon_id = %s;"
    execute_write(update_sql, tuple(params))
    return get_coupon_by_id(coupon_id), None


def delete_coupon(coupon_id, owner_id):
    """Deactivates a coupon owned by user."""
    existing = get_coupon_by_id(coupon_id)
    if not existing:
        return False, "Coupon not found"
    if int(existing["owner_id"]) != int(owner_id):
        return False, "Forbidden: You do not own this coupon"

    execute_write("UPDATE coupons SET status = 'REMOVED' WHERE coupon_id = %s;", (coupon_id,))
    return True, None


def search_coupons(params):
    """Searches and filters coupons dynamically with parameterized SQL."""
    conditions = ["c.expiry_date >= CURRENT_DATE()"]
    sql_params = []

    # Status filter
    status = params.get("status", "ACTIVE").upper()
    if status != "ALL":
        conditions.append("c.status = %s")
        sql_params.append(status)

    # Category & Brand
    if params.get("category_id"):
        conditions.append("c.category_id = %s")
        sql_params.append(int(params["category_id"]))
    if params.get("brand_id"):
        conditions.append("c.brand_id = %s")
        sql_params.append(int(params["brand_id"]))

    # Discount type & min
    if params.get("discount_type"):
        conditions.append("c.discount_type = %s")
        sql_params.append(params["discount_type"].upper())
    if params.get("min_discount"):
        conditions.append("c.discount_value >= %s")
        sql_params.append(float(params["min_discount"]))

    # Keyword search
    if params.get("keyword"):
        kw = f"%{params['keyword'].strip()}%"
        conditions.append("(c.title LIKE %s OR c.description LIKE %s OR cat.name LIKE %s OR b.name LIKE %s)")
        sql_params.extend([kw, kw, kw, kw])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Sort order
    sort_option = params.get("sort", "created_desc")
    sort_map = {
        "discount_desc": "c.discount_value DESC",
        "expiry_asc": "c.expiry_date ASC",
        "created_desc": "c.coupon_id DESC"
    }
    order_clause = f" ORDER BY {sort_map.get(sort_option, 'c.coupon_id DESC')}"

    sql = f"""
        SELECT c.*, cat.name AS category_name, b.name AS brand_name, u.name AS owner_name
        FROM coupons c
        JOIN categories cat ON c.category_id = cat.category_id
        JOIN brands b ON c.brand_id = b.brand_id
        JOIN users u ON c.owner_id = u.user_id
        {where_clause}
        {order_clause}
        LIMIT 100;
    """
    return execute_all(sql, tuple(sql_params))

"""
Exchange Request Service
Smart Coupon Swap System

Handles the full coupon-exchange lifecycle using the existing schema:
  swaps, swap_items, swap_history, notifications, coupons

NO new tables — uses only existing schema columns and status values.
"""

from datetime import datetime
from app.services.db import execute_one, execute_all, execute_write, execute_transaction
from app.services.coupon_service import get_coupon_by_id
from app.services.swap_service import calculate_swap_compatibility
from app.services.notification_service import create_notification


# ---------------------------------------------------------------------------
# CREATE EXCHANGE REQUEST
# ---------------------------------------------------------------------------

def create_exchange_request(initiator_id, offered_coupon_id, requested_coupon_id):
    """
    Creates a PROPOSED swap in the `swaps` table.

    Business rules enforced:
    - Initiator must own the offered coupon.
    - Initiator must NOT own the requested coupon.
    - Both coupons must be ACTIVE and not expired.
    - No duplicate PROPOSED swap for the same pair.

    Returns (swap_id, error_message).
    """
    offered = get_coupon_by_id(offered_coupon_id)
    requested = get_coupon_by_id(requested_coupon_id)

    if not offered:
        return None, "Offered coupon not found"
    if not requested:
        return None, "Requested coupon not found"

    if int(offered["owner_id"]) != int(initiator_id):
        return None, "You do not own the offered coupon"

    if int(requested["owner_id"]) == int(initiator_id):
        return None, "You cannot exchange a coupon with yourself"

    if offered["status"] != "ACTIVE":
        return None, "Your offered coupon is not active"
    if requested["status"] != "ACTIVE":
        return None, "The requested coupon is not active"

    today = datetime.today().strftime("%Y-%m-%d")
    if str(offered["expiry_date"]) < today:
        return None, "Your offered coupon has expired"
    if str(requested["expiry_date"]) < today:
        return None, "The requested coupon has expired"

    receiver_id = int(requested["owner_id"])

    # Duplicate prevention: check for an existing PROPOSED swap for this exact pair
    dup = execute_one(
        """SELECT swap_id FROM swaps
           WHERE initiator_id = %s
             AND offered_coupon_id = %s
             AND requested_coupon_id = %s
             AND status = 'PROPOSED';""",
        (initiator_id, offered_coupon_id, requested_coupon_id)
    )
    if dup:
        return None, "You already have a pending exchange request for this pair"

    # Calculate compatibility score (stored as 0.0000–1.0000 in schema)
    compat_result, _ = calculate_swap_compatibility(offered_coupon_id, requested_coupon_id)
    compat_score = None
    if compat_result:
        raw = compat_result["compatibility_score"]           # 0–100
        compat_score = round(float(raw) / 100.0, 4)         # convert to 0–1 for DB

    # Insert swap record
    swap_id, _ = execute_write(
        """INSERT INTO swaps
               (swap_type, initiator_id, receiver_id,
                offered_coupon_id, requested_coupon_id,
                compatibility_score, status, proposed_at)
           VALUES ('BILATERAL', %s, %s, %s, %s, %s, 'PROPOSED', NOW());""",
        (initiator_id, receiver_id,
         offered_coupon_id, requested_coupon_id, compat_score)
    )

    # Insert swap_history entry (PROPOSED)
    execute_write(
        """INSERT INTO swap_history
               (swap_id, previous_status, new_status, changed_by_user_id, notes)
           VALUES (%s, NULL, 'PROPOSED', %s, 'Exchange request created');""",
        (swap_id, initiator_id)
    )

    # Notify the coupon owner (receiver)
    initiator_name = execute_one(
        "SELECT name FROM users WHERE user_id = %s;", (initiator_id,)
    )
    initiator_name = initiator_name["name"] if initiator_name else "A user"
    score_display = round(float(compat_score or 0) * 100)

    create_notification(
        user_id=receiver_id,
        title="New Exchange Request",
        message=(
            f"{initiator_name} wants to exchange their "
            f"'{offered['title']}' for your '{requested['title']}'. "
            f"Compatibility: {score_display}/100."
        ),
        notif_type="SWAP_PROPOSAL"
    )

    return swap_id, None


# ---------------------------------------------------------------------------
# GET INCOMING EXCHANGE REQUESTS (for the logged-in receiver)
# ---------------------------------------------------------------------------

def get_incoming_requests(user_id):
    """
    Returns all PROPOSED swaps where the logged-in user is the receiver,
    enriched with coupon and requester details.
    """
    sql = """
        SELECT
            s.swap_id,
            s.initiator_id,
            s.offered_coupon_id,
            s.requested_coupon_id,
            s.compatibility_score,
            s.status,
            s.proposed_at,
            u.name          AS initiator_name,
            oc.title        AS offered_title,
            oc.discount_value  AS offered_value,
            oc.discount_type   AS offered_discount_type,
            oc.expiry_date     AS offered_expiry,
            ob.name            AS offered_brand,
            rc.title        AS requested_title,
            rc.discount_value  AS requested_value,
            rc.discount_type   AS requested_discount_type,
            rc.expiry_date     AS requested_expiry,
            rb.name            AS requested_brand
        FROM swaps s
        JOIN users u   ON u.user_id  = s.initiator_id
        JOIN coupons oc ON oc.coupon_id = s.offered_coupon_id
        JOIN brands  ob ON ob.brand_id  = oc.brand_id
        JOIN coupons rc ON rc.coupon_id = s.requested_coupon_id
        JOIN brands  rb ON rb.brand_id  = rc.brand_id
        WHERE s.receiver_id = %s
          AND s.status = 'PROPOSED'
        ORDER BY s.proposed_at DESC;
    """
    rows = execute_all(sql, (user_id,))
    for r in rows:
        r["compatibility_score"] = float(r["compatibility_score"]) if r.get("compatibility_score") else 0.0
        r["compatibility_pct"] = round(r["compatibility_score"] * 100)
        r["offered_value"]    = float(r["offered_value"]) if r.get("offered_value") else 0.0
        r["requested_value"]  = float(r["requested_value"]) if r.get("requested_value") else 0.0
        r["proposed_at"]      = str(r["proposed_at"]) if r.get("proposed_at") else ""
        r["offered_expiry"]   = str(r["offered_expiry"]) if r.get("offered_expiry") else ""
        r["requested_expiry"] = str(r["requested_expiry"]) if r.get("requested_expiry") else ""
    return rows


# ---------------------------------------------------------------------------
# GET OUTGOING EXCHANGE REQUESTS (sent by the logged-in user)
# ---------------------------------------------------------------------------

def get_outgoing_requests(user_id):
    """
    Returns swaps the logged-in user has initiated, in all statuses.
    """
    sql = """
        SELECT
            s.swap_id,
            s.receiver_id,
            s.offered_coupon_id,
            s.requested_coupon_id,
            s.compatibility_score,
            s.status,
            s.proposed_at,
            s.completed_at,
            u.name          AS receiver_name,
            oc.title        AS offered_title,
            rc.title        AS requested_title
        FROM swaps s
        JOIN users u   ON u.user_id    = s.receiver_id
        JOIN coupons oc ON oc.coupon_id = s.offered_coupon_id
        JOIN coupons rc ON rc.coupon_id = s.requested_coupon_id
        WHERE s.initiator_id = %s
        ORDER BY s.proposed_at DESC
        LIMIT 20;
    """
    rows = execute_all(sql, (user_id,))
    for r in rows:
        r["compatibility_score"] = float(r["compatibility_score"]) if r.get("compatibility_score") else 0.0
        r["proposed_at"]  = str(r["proposed_at"])  if r.get("proposed_at") else ""
        r["completed_at"] = str(r["completed_at"]) if r.get("completed_at") else None
    return rows


# ---------------------------------------------------------------------------
# ACCEPT EXCHANGE  (atomic transaction)
# ---------------------------------------------------------------------------

def accept_exchange(swap_id, receiver_id):
    """
    Accepts a PROPOSED swap:
    1. Re-validates ownership, coupon availability, and status.
    2. Transfers coupon ownership atomically.
    3. Marks swap as COMPLETED.
    4. Creates swap_items legs.
    5. Appends swap_history.
    6. Notifies both users.

    Returns (swap_row, error_message).
    """
    swap = execute_one(
        """SELECT * FROM swaps WHERE swap_id = %s;""", (swap_id,)
    )
    if not swap:
        return None, "Exchange request not found"
    if int(swap["receiver_id"]) != int(receiver_id):
        return None, "Forbidden: You are not the recipient of this request"
    if swap["status"] != "PROPOSED":
        return None, f"Exchange is already {swap['status']} and cannot be accepted"

    offered   = get_coupon_by_id(swap["offered_coupon_id"])
    requested = get_coupon_by_id(swap["requested_coupon_id"])

    if not offered or not requested:
        return None, "One or both coupons no longer exist"
    if offered["status"] != "ACTIVE":
        return None, "The offered coupon is no longer active"
    if requested["status"] != "ACTIVE":
        return None, "Your coupon is no longer active"

    today = datetime.today().strftime("%Y-%m-%d")
    if str(offered["expiry_date"]) < today:
        return None, "The offered coupon has expired"
    if str(requested["expiry_date"]) < today:
        return None, "Your coupon has expired"

    initiator_id = int(swap["initiator_id"])
    offered_id   = int(swap["offered_coupon_id"])
    requested_id = int(swap["requested_coupon_id"])

    # Build atomic transaction steps
    steps = [
        # 1. Mark swap COMPLETED
        (
            "UPDATE swaps SET status='COMPLETED', completed_at=NOW() WHERE swap_id=%s;",
            (swap_id,)
        ),
        # 2. Transfer offered coupon to receiver (new owner = receiver_id)
        (
            "UPDATE coupons SET owner_id=%s, status='SWAPPED' WHERE coupon_id=%s;",
            (receiver_id, offered_id)
        ),
        # 3. Transfer requested coupon to initiator (new owner = initiator_id)
        (
            "UPDATE coupons SET owner_id=%s, status='SWAPPED' WHERE coupon_id=%s;",
            (initiator_id, requested_id)
        ),
        # 4. swap_items leg A: offered coupon travels initiator → receiver
        (
            """INSERT INTO swap_items (swap_id, from_user_id, to_user_id, coupon_id, status)
               VALUES (%s, %s, %s, %s, 'CONFIRMED');""",
            (swap_id, initiator_id, receiver_id, offered_id)
        ),
        # 5. swap_items leg B: requested coupon travels receiver → initiator
        (
            """INSERT INTO swap_items (swap_id, from_user_id, to_user_id, coupon_id, status)
               VALUES (%s, %s, %s, %s, 'CONFIRMED');""",
            (swap_id, receiver_id, initiator_id, requested_id)
        ),
        # 6. History: PROPOSED → COMPLETED
        (
            """INSERT INTO swap_history
                   (swap_id, previous_status, new_status, changed_by_user_id, notes)
               VALUES (%s, 'PROPOSED', 'COMPLETED', %s, 'Exchange accepted and completed');""",
            (swap_id, receiver_id)
        ),
    ]

    try:
        execute_transaction(steps)
    except Exception as ex:
        return None, f"Database error during exchange: {str(ex)}"

    # Fetch user names for notifications
    initiator = execute_one("SELECT name FROM users WHERE user_id=%s;", (initiator_id,))
    receiver  = execute_one("SELECT name FROM users WHERE user_id=%s;", (receiver_id,))
    init_name = initiator["name"] if initiator else "User"
    recv_name = receiver["name"]  if receiver  else "User"

    # Notify initiator: their request was accepted
    create_notification(
        user_id=initiator_id,
        title="Exchange Accepted!",
        message=(
            f"{recv_name} accepted your exchange. "
            f"'{offered['title']}' → {recv_name} | "
            f"'{requested['title']}' → You."
        ),
        notif_type="SWAP_ACCEPTED"
    )
    # Notify receiver: confirmation
    create_notification(
        user_id=receiver_id,
        title="Exchange Completed!",
        message=(
            f"Exchange complete with {init_name}. "
            f"'{requested['title']}' → {init_name} | "
            f"'{offered['title']}' → You."
        ),
        notif_type="SWAP_COMPLETED"
    )

    return execute_one("SELECT * FROM swaps WHERE swap_id=%s;", (swap_id,)), None


# ---------------------------------------------------------------------------
# REJECT EXCHANGE
# ---------------------------------------------------------------------------

def reject_exchange(swap_id, receiver_id):
    """
    Rejects a PROPOSED swap.
    Does not change coupon ownership.
    Notifies the initiator.

    Returns (swap_id, error_message).
    """
    swap = execute_one("SELECT * FROM swaps WHERE swap_id = %s;", (swap_id,))
    if not swap:
        return None, "Exchange request not found"
    if int(swap["receiver_id"]) != int(receiver_id):
        return None, "Forbidden: You are not the recipient of this request"
    if swap["status"] != "PROPOSED":
        return None, f"Exchange is already {swap['status']}"

    execute_write(
        "UPDATE swaps SET status='REJECTED' WHERE swap_id=%s;", (swap_id,)
    )
    execute_write(
        """INSERT INTO swap_history
               (swap_id, previous_status, new_status, changed_by_user_id, notes)
           VALUES (%s, 'PROPOSED', 'REJECTED', %s, 'Exchange rejected by recipient');""",
        (swap_id, receiver_id)
    )

    # Notify initiator
    offered   = get_coupon_by_id(int(swap["offered_coupon_id"]))
    requested = get_coupon_by_id(int(swap["requested_coupon_id"]))
    receiver_row = execute_one("SELECT name FROM users WHERE user_id=%s;", (receiver_id,))
    recv_name = receiver_row["name"] if receiver_row else "The other user"

    create_notification(
        user_id=int(swap["initiator_id"]),
        title="Exchange Request Rejected",
        message=(
            f"{recv_name} declined your exchange of "
            f"'{offered['title'] if offered else '?'}' "
            f"for '{requested['title'] if requested else '?'}'."
        ),
        notif_type="SWAP_REJECTED"
    )

    return swap_id, None

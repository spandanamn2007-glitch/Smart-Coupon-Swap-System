"""
Phase 9 Automated Test Suite — Coupon Exchange Request Flow
Smart Coupon Swap System

Tests:
1. Exchange request creation and notification to recipient
2. Recipient can see incoming exchange requests on Dashboard API
3. Accept exchange flow (atomic swap, ownership transfer, notifications, swap_items, history)
4. Reject exchange flow (no ownership transfer, notification sent, status REJECTED)
5. Duplicate pending exchange request prevention
6. Invalid exchange boundaries (self-exchange, not owning offered coupon, non-existent coupon, non-recipient accept)
"""

import pytest
from datetime import datetime, timedelta
from app import create_app
from app.config import TestingConfig
from app.services.db import execute_one, execute_all, execute_write


@pytest.fixture
def app():
    return create_app(TestingConfig)


@pytest.fixture
def client(app):
    return app.test_client()


def _setup_test_user_and_coupon(client, name, email, password, coupon_title, discount=20.0):
    """Helper to create a user, log them in, and create a coupon."""
    # Clean previous data for email
    execute_write("DELETE FROM swap_history WHERE swap_id IN (SELECT swap_id FROM swaps WHERE initiator_id IN (SELECT user_id FROM users WHERE email=%s) OR receiver_id IN (SELECT user_id FROM users WHERE email=%s));", (email, email))
    execute_write("DELETE FROM swap_items WHERE from_user_id IN (SELECT user_id FROM users WHERE email=%s) OR to_user_id IN (SELECT user_id FROM users WHERE email=%s);", (email, email))
    execute_write("DELETE FROM swaps WHERE initiator_id IN (SELECT user_id FROM users WHERE email=%s) OR receiver_id IN (SELECT user_id FROM users WHERE email=%s);", (email, email))
    execute_write("DELETE FROM notifications WHERE user_id IN (SELECT user_id FROM users WHERE email=%s);", (email,))
    execute_write("DELETE FROM coupons WHERE owner_id IN (SELECT user_id FROM users WHERE email=%s);", (email,))
    execute_write("DELETE FROM user_general_preferences WHERE user_id IN (SELECT user_id FROM users WHERE email=%s);", (email,))
    execute_write("DELETE FROM users WHERE email=%s;", (email,))

    # Register
    reg = client.post("/api/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
        "city": "Bengaluru",
        "state": "Karnataka"
    })
    assert reg.status_code == 201

    # Login
    login = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login.status_code == 200
    user_id = login.get_json()["user"]["user_id"]

    # Create coupon
    future_date = (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    today_date = datetime.today().strftime("%Y-%m-%d")
    c_res = client.post("/api/coupons", json={
        "title": coupon_title,
        "description": f"Test coupon for {name}",
        "category_id": 1,
        "brand_id": 1,
        "coupon_code": f"CODE_{datetime.now().microsecond}",
        "discount_type": "PERCENTAGE",
        "discount_value": discount,
        "issue_date": today_date,
        "expiry_date": future_date
    })
    assert c_res.status_code == 201
    coupon_id = c_res.get_json()["coupon"]["coupon_id"]

    return user_id, coupon_id


def test_create_exchange_request_and_see_request(client):
    """Test User A requests User B's coupon, User B sees it in /api/swaps/requests, and notification is sent."""
    # Setup User A
    user_a_id, coupon_a_id = _setup_test_user_and_coupon(
        client, "Spandana Test", "spandana_test@smartswap.local", "Password123!", "Swiggy 200 Off", 25.0
    )

    # Setup User B in a separate test client
    app_instance = client.application
    client_b = app_instance.test_client()
    user_b_id, coupon_b_id = _setup_test_user_and_coupon(
        client_b, "Sowmya Test", "sowmya_test@smartswap.local", "Password123!", "PUMA 20 Off", 20.0
    )

    # User B (Sowmya) offers Coupon B for User A's Coupon A
    req_res = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert req_res.status_code == 201
    data = req_res.get_json()
    assert "swap_id" in data
    swap_id = data["swap_id"]

    # Verify User A (recipient/Spandana) sees the incoming request
    list_res = client.get("/api/swaps/requests")
    assert list_res.status_code == 200
    list_data = list_res.get_json()
    incoming = list_data.get("incoming", [])
    assert any(r["swap_id"] == swap_id for r in incoming)

    matched = next(r for r in incoming if r["swap_id"] == swap_id)
    assert matched["initiator_name"] == "Sowmya Test"
    assert matched["offered_title"] == "PUMA 20 Off"
    assert matched["requested_title"] == "Swiggy 200 Off"
    assert matched["status"] == "PROPOSED"
    assert matched["compatibility_score"] > 0

    # Verify User A received a notification
    notif_res = client.get("/api/notifications")
    assert notif_res.status_code == 200
    notifs = notif_res.get_json().get("notifications", [])
    assert any("Sowmya Test wants to exchange" in n["message"] for n in notifs)


def test_accept_exchange_flow(client):
    """Test User A accepts User B's exchange proposal, ownership transfers, status COMPLETED."""
    app_instance = client.application
    client_b = app_instance.test_client()

    user_a_id, coupon_a_id = _setup_test_user_and_coupon(
        client, "User A Accept", "usera_accept@smartswap.local", "Password123!", "Coupon Alpha", 30.0
    )
    user_b_id, coupon_b_id = _setup_test_user_and_coupon(
        client_b, "User B Propose", "userb_propose@smartswap.local", "Password123!", "Coupon Beta", 30.0
    )

    # User B proposes
    req_res = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert req_res.status_code == 201
    swap_id = req_res.get_json()["swap_id"]

    # User A accepts
    accept_res = client.post(f"/api/swaps/requests/{swap_id}/accept")
    assert accept_res.status_code == 200
    assert accept_res.get_json()["swap"]["status"] == "COMPLETED"

    # Verify coupon ownership swapped in database!
    coupon_a_db = execute_one("SELECT owner_id, status FROM coupons WHERE coupon_id=%s;", (coupon_a_id,))
    coupon_b_db = execute_one("SELECT owner_id, status FROM coupons WHERE coupon_id=%s;", (coupon_b_id,))

    # Coupon A was originally owned by User A; now owned by User B!
    assert coupon_a_db["owner_id"] == user_b_id
    assert coupon_a_db["status"] == "SWAPPED"

    # Coupon B was originally owned by User B; now owned by User A!
    assert coupon_b_db["owner_id"] == user_a_id
    assert coupon_b_db["status"] == "SWAPPED"

    # Verify swap_items records
    items = execute_all("SELECT * FROM swap_items WHERE swap_id=%s;", (swap_id,))
    assert len(items) == 2
    assert all(item["status"] == "CONFIRMED" for item in items)

    # Verify swap_history records
    history = execute_all("SELECT * FROM swap_history WHERE swap_id=%s ORDER BY history_id ASC;", (swap_id,))
    assert any(h["new_status"] == "COMPLETED" for h in history)

    # Verify cannot accept again (already completed)
    re_accept = client.post(f"/api/swaps/requests/{swap_id}/accept")
    assert re_accept.status_code in [400, 403, 404]

    # Verify both received notifications
    notif_a = client.get("/api/notifications").get_json()["notifications"]
    notif_b = client_b.get("/api/notifications").get_json()["notifications"]
    assert any(n["type"] == "SWAP_COMPLETED" for n in notif_a)
    assert any(n["type"] == "SWAP_ACCEPTED" for n in notif_b)


def test_reject_exchange_flow(client):
    """Test User A rejects User B's proposal, ownership unchanged, status REJECTED."""
    app_instance = client.application
    client_b = app_instance.test_client()

    user_a_id, coupon_a_id = _setup_test_user_and_coupon(
        client, "User A Reject", "usera_reject@smartswap.local", "Password123!", "Coupon X", 15.0
    )
    user_b_id, coupon_b_id = _setup_test_user_and_coupon(
        client_b, "User B Propose Reject", "userb_reject@smartswap.local", "Password123!", "Coupon Y", 15.0
    )

    req_res = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert req_res.status_code == 201
    swap_id = req_res.get_json()["swap_id"]

    # User A rejects
    rej_res = client.post(f"/api/swaps/requests/{swap_id}/reject")
    assert rej_res.status_code == 200

    # Verify swap is REJECTED
    swap_db = execute_one("SELECT status FROM swaps WHERE swap_id=%s;", (swap_id,))
    assert swap_db["status"] == "REJECTED"

    # Verify coupon ownership did NOT change
    c_a = execute_one("SELECT owner_id, status FROM coupons WHERE coupon_id=%s;", (coupon_a_id,))
    c_b = execute_one("SELECT owner_id, status FROM coupons WHERE coupon_id=%s;", (coupon_b_id,))
    assert c_a["owner_id"] == user_a_id
    assert c_b["owner_id"] == user_b_id
    assert c_a["status"] == "ACTIVE"
    assert c_b["status"] == "ACTIVE"

    # Verify initiator received rejection notification
    notif_b = client_b.get("/api/notifications").get_json()["notifications"]
    assert any(n["type"] == "SWAP_REJECTED" for n in notif_b)


def test_duplicate_exchange_request_prevention(client):
    """Test duplicate exchange proposals for the same pair while pending are blocked."""
    app_instance = client.application
    client_b = app_instance.test_client()

    _, coupon_a_id = _setup_test_user_and_coupon(
        client, "User A Dup", "usera_dup@smartswap.local", "Password123!", "Coupon Dup A", 20.0
    )
    _, coupon_b_id = _setup_test_user_and_coupon(
        client_b, "User B Dup", "userb_dup@smartswap.local", "Password123!", "Coupon Dup B", 20.0
    )

    # First proposal succeeds
    res1 = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert res1.status_code == 201

    # Second duplicate proposal fails with 400
    res2 = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert res2.status_code == 400
    assert "already have a pending exchange request" in res2.get_json()["error"]


def test_invalid_exchange_boundaries(client):
    """Test edge cases: cannot exchange own coupon, cannot offer someone else's coupon, etc."""
    app_instance = client.application
    client_b = app_instance.test_client()

    _, coupon_a_id = _setup_test_user_and_coupon(
        client, "User A Edge", "usera_edge@smartswap.local", "Password123!", "Coupon Edge A", 20.0
    )
    # Create a second coupon for User A
    c2 = client.post("/api/coupons", json={
        "title": "Coupon Edge A2",
        "category_id": 1,
        "brand_id": 1,
        "coupon_code": "EDGE_A2",
        "discount_type": "PERCENTAGE",
        "discount_value": 20.0,
        "issue_date": datetime.today().strftime("%Y-%m-%d"),
        "expiry_date": (datetime.today() + timedelta(days=30)).strftime("%Y-%m-%d")
    })
    coupon_a2_id = c2.get_json()["coupon"]["coupon_id"]

    # 1. User A tries to swap two of their own coupons
    res_self = client.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_a_id,
        "requested_coupon_id": coupon_a2_id
    })
    assert res_self.status_code == 400
    assert "yourself" in res_self.get_json()["error"]

    # 2. User B tries to offer User A's coupon (that User B doesn't own)
    _, coupon_b_id = _setup_test_user_and_coupon(
        client_b, "User B Edge", "userb_edge@smartswap.local", "Password123!", "Coupon Edge B", 20.0
    )
    res_not_owner = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_a_id,  # Owned by User A
        "requested_coupon_id": coupon_b_id
    })
    assert res_not_owner.status_code == 400
    assert "not own" in res_not_owner.get_json()["error"]

    # 3. Non-recipient tries to accept a swap
    res_valid = client_b.post("/api/swaps/requests", json={
        "offered_coupon_id": coupon_b_id,
        "requested_coupon_id": coupon_a_id
    })
    assert res_valid.status_code == 201
    swap_id = res_valid.get_json()["swap_id"]

    # User B (initiator) tries to accept their own proposal
    res_wrong_accept = client_b.post(f"/api/swaps/requests/{swap_id}/accept")
    assert res_wrong_accept.status_code == 403

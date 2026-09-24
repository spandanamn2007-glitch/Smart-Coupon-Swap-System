"""
Phase 7 Automated Test Suite
Smart Coupon Swap System

Tests:
1. Coupon Marketplace CRUD (Create, List, Detail, Update, Delete)
2. Search & Filtering with Parameterized SQL
3. Explainable Recommendations System & Reasons
4. Bilateral 2-Way Swap Compatibility Scoring & Boundary Checks
5. 3-Way / Multi-User Circular Swap Cycle Graph Engine
6. Fraud / Anomaly Detection Pipeline
7. Swap Acceptance Prediction ML Model
8. Category Demand Forecasting Model
9. Notifications API
"""

import os
import pytest
from app import create_app
from app.config import TestingConfig
from app.services.db import execute_one, execute_write

@pytest.fixture
def app():
    return create_app(TestingConfig)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Fixture providing an authenticated test client session."""
    test_email = "phase7_user@smartswap.local"
    test_pass = "Password123!"

    # Clean up and register/login user
    execute_write("DELETE FROM notifications WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM coupons WHERE owner_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM user_general_preferences WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM users WHERE email = %s;", (test_email,))

    reg_res = client.post("/api/auth/register", json={
        "name": "Phase7 Tester",
        "email": test_email,
        "password": test_pass,
        "city": "Bengaluru",
        "state": "Karnataka"
    })
    assert reg_res.status_code == 201

    login_res = client.post("/api/auth/login", json={"email": test_email, "password": test_pass})
    assert login_res.status_code == 200
    return client

# ==============================================================================
# 1. COUPON MARKETPLACE & SEARCH TESTS
# ==============================================================================

def test_coupon_crud_and_search(auth_client):
    """Test Coupon CRUD, Authorization Boundaries, and Search/Filtering."""
    # Create coupon
    payload = {
        "category_id": 1,
        "brand_id": 1,
        "discount_type": "PERCENTAGE",
        "discount_value": 20.0,
        "min_purchase_amount": 500.0,
        "issue_date": "2026-01-01",
        "expiry_date": "2026-12-31",
        "title": "20% Off Fast Food Voucher",
        "description": "Valid on orders above 500",
        "coupon_code": "pytest_c1"
    }
    create_res = auth_client.post("/api/coupons", json=payload)
    assert create_res.status_code == 201
    c_data = create_res.get_json()["coupon"]
    coupon_id = c_data["coupon_id"]

    # View single coupon detail
    detail_res = auth_client.get(f"/api/coupons/{coupon_id}")
    assert detail_res.status_code == 200
    assert detail_res.get_json()["coupon"]["title"] == payload["title"]

    # Search / Filter
    search_res = auth_client.get("/api/coupons?category_id=1&keyword=Fast")
    assert search_res.status_code == 200
    assert search_res.get_json()["count"] >= 1

    # Update own coupon
    update_res = auth_client.put(f"/api/coupons/{coupon_id}", json={"title": "Updated Title"})
    assert update_res.status_code == 200

    # Delete coupon
    del_res = auth_client.delete(f"/api/coupons/{coupon_id}")
    assert del_res.status_code == 200

# ==============================================================================
# 2. RECOMMENDATION SYSTEM TESTS
# ==============================================================================

def test_recommendations(auth_client):
    """Test explainable recommendations endpoint."""
    rec_res = auth_client.get("/api/recommendations")
    assert rec_res.status_code == 200
    data = rec_res.get_json()
    assert "recommendations" in data
    if data["count"] > 0:
        first_rec = data["recommendations"][0]
        assert "recommendation_score" in first_rec
        assert "explanation" in first_rec

# ==============================================================================
# 3. SMART 2-WAY SWAP & 3-WAY CYCLE TESTS
# ==============================================================================

def test_swap_compatibility(client):
    """Test bilateral swap compatibility calculation and boundary checks."""
    # Rejection check: same user coupon or invalid ID
    res = client.post("/api/swaps/compatibility", json={"offered_coupon_id": 99999, "requested_coupon_id": 99998})
    assert res.status_code == 400

def test_swap_cycles(client):
    """Test 3-way circular swap cycle graph detection."""
    res = client.get("/api/swaps/cycles")
    assert res.status_code == 200
    assert "cycles" in res.get_json()

# ==============================================================================
# 4. MACHINE LEARNING PREDICTION TESTS
# ==============================================================================

def test_acceptance_prediction(client):
    """Test swap acceptance probability model prediction."""
    payload = {
        "offered_value": 1500.0,
        "requested_value": 1450.0,
        "category_match": 1,
        "brand_match": 0,
        "proposer_rating": 4.5,
        "receiver_rating": 4.0
    }
    res = client.post("/api/predictions/acceptance", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "acceptance_probability" in data
    assert 0.0 <= data["acceptance_probability"] <= 1.0

def test_anomaly_detection(client):
    """Test IsolationForest user anomaly detection endpoint."""
    res = client.get("/api/predictions/anomalies")
    assert res.status_code == 200
    assert "anomalous_users" in res.get_json()

def test_demand_forecasting(client):
    """Test category demand regression forecast endpoint."""
    res = client.post("/api/predictions/demand", json={"prev_month_requests": 150})
    assert res.status_code == 200
    assert "forecasted_next_month_requests" in res.get_json()

# ==============================================================================
# 5. NOTIFICATIONS TESTS
# ==============================================================================

def test_notifications(auth_client):
    """Test creating and retrieving system notifications."""
    notif_payload = {
        "title": "Swap Opportunity Detected",
        "message": "A 3-way swap cycle matching your requested coupon is available.",
        "type": "SMART_MATCH_FOUND"
    }
    create_res = auth_client.post("/api/notifications", json=notif_payload)
    assert create_res.status_code == 201

    get_res = auth_client.get("/api/notifications")
    assert get_res.status_code == 200
    assert get_res.get_json()["count"] >= 1

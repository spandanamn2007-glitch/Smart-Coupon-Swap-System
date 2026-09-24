"""
Phase 8 Automated Test Suite
Smart Coupon Swap System

Tests:
1. Dashboard page routing & auth guards
2. Admin API stats endpoint (auth & role boundaries)
3. Health check
4. Unauthorized access to protected endpoints
5. Invalid input handling
6. Existing Phase 6/7 API integration (regression)
"""

import pytest
from app import create_app
from app.config import TestingConfig
from app.services.db import execute_one, execute_write


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def app():
    return create_app(TestingConfig)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Authenticated regular user client (role_id=2)."""
    test_email = "phase8_user@smartswap.local"
    test_pass = "Password123!"

    # Cleanup
    execute_write("DELETE FROM notifications WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM coupons WHERE owner_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM user_general_preferences WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM users WHERE email = %s;", (test_email,))

    reg = client.post("/api/auth/register", json={
        "name": "Phase8 Tester", "email": test_email,
        "password": test_pass, "city": "Bengaluru", "state": "Karnataka"
    })
    assert reg.status_code == 201

    login = client.post("/api/auth/login", json={"email": test_email, "password": test_pass})
    assert login.status_code == 200
    return client


@pytest.fixture
def admin_client(client):
    """Authenticated admin user client (role_id=1)."""
    test_email = "phase8_admin@smartswap.local"
    test_pass = "AdminPass123!"

    # Cleanup
    execute_write("DELETE FROM notifications WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM coupons WHERE owner_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM user_general_preferences WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM users WHERE email = %s;", (test_email,))

    reg = client.post("/api/auth/register", json={
        "name": "Phase8 Admin", "email": test_email,
        "password": test_pass, "city": "Mumbai", "state": "Maharashtra",
        "role_id": 1
    })
    assert reg.status_code == 201

    login = client.post("/api/auth/login", json={"email": test_email, "password": test_pass})
    assert login.status_code == 200
    return client


# ==============================================================================
# 1. HEALTH CHECK
# ==============================================================================

def test_health_check(client):
    """GET /health returns 200 with 'status' key."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data


# ==============================================================================
# 2. DASHBOARD PAGE ROUTING
# ==============================================================================

def test_dashboard_root_unauthenticated_redirects(client):
    """GET / serves the landing page without error."""
    res = client.get("/")
    assert res.status_code == 200


def test_dashboard_user_unauthenticated_redirects(client):
    """GET /dashboard without session should redirect (302) to login."""
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code in (302, 401)


def test_dashboard_analytics_unauthenticated_redirects(client):
    """GET /dashboard/analytics without session should redirect (302) to login."""
    res = client.get("/dashboard/analytics", follow_redirects=False)
    assert res.status_code in (302, 401)


def test_dashboard_admin_unauthenticated_redirects(client):
    """GET /dashboard/admin without session should redirect (302) to login."""
    res = client.get("/dashboard/admin", follow_redirects=False)
    assert res.status_code in (302, 401)


def test_dashboard_user_authenticated_ok(auth_client):
    """GET /dashboard with auth returns 200."""
    res = auth_client.get("/dashboard")
    assert res.status_code == 200


def test_dashboard_analytics_authenticated_ok(auth_client):
    """GET /dashboard/analytics with auth returns 200."""
    res = auth_client.get("/dashboard/analytics")
    assert res.status_code == 200


def test_dashboard_admin_non_admin_returns_403(auth_client):
    """GET /dashboard/admin with non-admin role_id=2 returns 403 page."""
    res = auth_client.get("/dashboard/admin")
    assert res.status_code == 403


def test_dashboard_admin_admin_role_ok(admin_client):
    """GET /dashboard/admin with admin role returns 200."""
    res = admin_client.get("/dashboard/admin")
    assert res.status_code == 200


# ==============================================================================
# 3. ADMIN STATS API
# ==============================================================================

def test_admin_stats_unauthenticated(client):
    """GET /api/admin/stats without session returns 401."""
    res = client.get("/api/admin/stats")
    assert res.status_code == 401


def test_admin_stats_non_admin_forbidden(auth_client):
    """GET /api/admin/stats with role_id=2 returns 403."""
    res = auth_client.get("/api/admin/stats")
    assert res.status_code == 403


def test_admin_stats_admin_returns_data(admin_client):
    """GET /api/admin/stats with admin role returns stats dict."""
    res = admin_client.get("/api/admin/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert "stats" in data
    stats = data["stats"]
    assert "total_users" in stats
    assert "total_coupons" in stats
    assert "total_swaps" in stats
    assert "total_requests" in stats
    assert "open_reports" in stats


# ==============================================================================
# 4. UNAUTHORIZED ACCESS BOUNDARIES
# ==============================================================================

def test_unauthorized_profile(client):
    """GET /api/users/profile without session returns 401."""
    res = client.get("/api/users/profile")
    assert res.status_code == 401


def test_unauthorized_notifications(client):
    """GET /api/notifications without session returns 401."""
    res = client.get("/api/notifications")
    assert res.status_code == 401


def test_unauthorized_coupon_create(client):
    """POST /api/coupons without session returns 401."""
    res = client.post("/api/coupons", json={"title": "Test"})
    assert res.status_code == 401


def test_unauthorized_notification_mark_read(client):
    """PUT /api/notifications/99999/read without session returns 401."""
    res = client.put("/api/notifications/99999/read")
    assert res.status_code == 401


# ==============================================================================
# 5. INVALID INPUT HANDLING
# ==============================================================================

def test_invalid_login_missing_fields(client):
    """POST /api/auth/login with empty JSON returns 400."""
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400


def test_invalid_login_wrong_credentials(client):
    """POST /api/auth/login with wrong password returns 401."""
    res = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong"})
    assert res.status_code == 401


def test_invalid_register_missing_fields(client):
    """POST /api/auth/register with missing fields returns 400."""
    res = client.post("/api/auth/register", json={"email": "test@test.com"})
    assert res.status_code == 400


def test_invalid_register_bad_email(client):
    """POST /api/auth/register with invalid email returns 400."""
    res = client.post("/api/auth/register", json={"name": "X", "email": "notanemail", "password": "pass123"})
    assert res.status_code == 400


def test_invalid_acceptance_prediction_missing_fields(client):
    """POST /api/predictions/acceptance with empty JSON returns 400."""
    res = client.post("/api/predictions/acceptance", json={})
    assert res.status_code == 400


def test_invalid_demand_prediction_missing_field(client):
    """POST /api/predictions/demand with empty JSON returns 400."""
    res = client.post("/api/predictions/demand", json={})
    assert res.status_code == 400


def test_coupon_not_found(client):
    """GET /api/coupons/99999999 returns 404."""
    res = client.get("/api/coupons/99999999")
    assert res.status_code == 404


def test_swap_compatibility_nonexistent_ids(client):
    """POST /api/swaps/compatibility with non-existent coupon IDs returns 400."""
    res = client.post("/api/swaps/compatibility", json={"offered_coupon_id": 99999, "requested_coupon_id": 99998})
    assert res.status_code == 400


# ==============================================================================
# 6. EXISTING PHASE 7 API REGRESSION
# ==============================================================================

def test_coupons_list_returns_ok(client):
    """GET /api/coupons (public browse) returns 200."""
    res = client.get("/api/coupons")
    assert res.status_code == 200
    data = res.get_json()
    assert "coupons" in data
    assert "count" in data


def test_swap_cycles_returns_ok(client):
    """GET /api/swaps/cycles returns 200 with cycles key."""
    res = client.get("/api/swaps/cycles")
    assert res.status_code == 200
    assert "cycles" in res.get_json()


def test_acceptance_prediction_valid_input(client):
    """POST /api/predictions/acceptance with valid data returns probability 0-1."""
    res = client.post("/api/predictions/acceptance", json={
        "offered_value": 1200.0, "requested_value": 1100.0,
        "category_match": 1, "brand_match": 0,
        "proposer_rating": 4.0, "receiver_rating": 3.5
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "acceptance_probability" in data
    assert 0.0 <= data["acceptance_probability"] <= 1.0


def test_anomaly_detection_returns_ok(client):
    """GET /api/predictions/anomalies returns 200 with anomalous_users key."""
    res = client.get("/api/predictions/anomalies")
    assert res.status_code == 200
    assert "anomalous_users" in res.get_json()


def test_demand_forecast_valid_input(client):
    """POST /api/predictions/demand with valid data returns forecast."""
    res = client.post("/api/predictions/demand", json={"prev_month_requests": 100})
    assert res.status_code == 200
    assert "forecasted_next_month_requests" in res.get_json()


def test_recommendations_authenticated(auth_client):
    """GET /api/recommendations with auth returns 200 and list."""
    res = auth_client.get("/api/recommendations")
    assert res.status_code == 200
    assert "recommendations" in res.get_json()


def test_notifications_authenticated(auth_client):
    """GET /api/notifications with auth returns 200."""
    res = auth_client.get("/api/notifications")
    assert res.status_code == 200
    assert "notifications" in res.get_json()

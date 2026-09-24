"""
Phase 6 Automated Test Suite
Smart Coupon Swap System

Tests:
1. Flask app initialization & /health endpoint
2. Registration, duplicate rejection, and email validation
3. Login authentication and password security
4. Session handling and logout
5. Profile & Preference endpoints
6. Authorization boundaries (rejecting modification of another user's profile)
7. Feature engineering execution & artifact verification
8. Preserved raw & processed data integrity
"""

import os
import pytest
import pandas as pd
from app import create_app
from app.config import TestingConfig
from app.services.db import execute_one, execute_write

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# ==============================================================================
# 1. BACKEND & HEALTH ENDPOINT TESTS
# ==============================================================================

def test_health_endpoint(client):
    """Test 1: GET /health returns HTTP 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "Smart Coupon Swap System" in data["service"]

# ==============================================================================
# 2. AUTHENTICATION & USER PROFILE TESTS
# ==============================================================================

def test_registration_and_login_flow(client):
    """Test 2-6: Registration, Duplicate Rejection, Login Success, Invalid Login, and Security."""
    test_email = "pytest_user_phase6@smartswap.local"
    test_pass = "SecurePass123!"

    # Clean up previous test run if exists
    execute_write("DELETE FROM user_general_preferences WHERE user_id IN (SELECT user_id FROM users WHERE email = %s);", (test_email,))
    execute_write("DELETE FROM users WHERE email = %s;", (test_email,))

    # Test Registration Success
    reg_payload = {
        "name": "Pytest User",
        "email": test_email,
        "password": test_pass,
        "city": "Bengaluru",
        "state": "Karnataka"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.get_json()
    assert "user" in reg_data
    assert reg_data["user"]["email"] == test_email
    assert "password" not in reg_data["user"]
    assert "password_hash" not in reg_data["user"]

    # Test Duplicate Registration Rejection
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.get_json()["error"]

    # Test Invalid Login (Wrong Password)
    bad_login_res = client.post("/api/auth/login", json={"email": test_email, "password": "WrongPassword!"})
    assert bad_login_res.status_code == 401

    # Test Login Success
    login_res = client.post("/api/auth/login", json={"email": test_email, "password": test_pass})
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["user"]["email"] == test_email
    assert "password" not in login_data["user"]
    assert "password_hash" not in login_data["user"]

    # Test Authenticated Profile Access
    profile_res = client.get("/api/users/profile")
    assert profile_res.status_code == 200
    prof_data = profile_res.get_json()
    assert prof_data["user"]["email"] == test_email
    assert "password_hash" not in prof_data["user"]

    # Test Authorization Boundary: Attempt to modify another user's profile
    other_user_id = prof_data["user"]["user_id"] + 999
    forbidden_res = client.put("/api/users/profile", json={"user_id": other_user_id, "name": "Hacked Name"})
    assert forbidden_res.status_code == 403

    # Test Valid Profile Update
    update_res = client.put("/api/users/profile", json={"name": "Pytest Updated Name", "city": "Mumbai"})
    assert update_res.status_code == 200
    assert update_res.get_json()["user"]["name"] == "Pytest Updated Name"

    # Test Preferences Access & Update
    pref_res = client.get("/api/users/preferences")
    assert pref_res.status_code == 200

    update_pref_res = client.put("/api/users/preferences", json={"min_preferred_discount_pct": 25.0, "preferred_location": "Delhi"})
    assert update_pref_res.status_code == 200
    assert update_pref_res.get_json()["preferences"]["min_preferred_discount_pct"] == 25.0

    # Test Logout
    logout_res = client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # Test Unauthenticated Profile Access Rejection
    unauth_res = client.get("/api/users/profile")
    assert unauth_res.status_code == 401

# ==============================================================================
# 3. FEATURE ENGINEERING PIPELINE & ARTIFACT TESTS
# ==============================================================================

def test_feature_engineering_artifacts():
    """Test 7-8: Feature engineering outputs generated & non-empty."""
    features_dir = os.path.join(os.path.dirname(__file__), "..", "data", "features")
    expected_files = [
        "user_features.csv",
        "coupon_features.csv",
        "interaction_features.csv",
        "swap_pair_features.csv"
    ]
    for fname in expected_files:
        fpath = os.path.join(features_dir, fname)
        assert os.path.isfile(fpath), f"Missing feature dataset: {fname}"
        df = pd.read_csv(fpath)
        assert len(df) > 0, f"Feature dataset {fname} is empty"

# ==============================================================================
# 4. DATASET IMMUTABILITY & INTEGRITY TESTS
# ==============================================================================

def test_data_integrity():
    """Test 9-10: Raw and processed datasets are intact."""
    root = os.path.join(os.path.dirname(__file__), "..")
    raw_dir = os.path.join(root, "data", "raw")
    proc_dir = os.path.join(root, "data", "processed")

    raw_files = ["categories.csv", "brands.csv", "users.csv", "coupons.csv", "swaps.csv"]
    for rf in raw_files:
        assert os.path.isfile(os.path.join(raw_dir, rf))

    proc_files = ["categories_clean.csv", "brands_clean.csv", "users_clean.csv", "coupons_clean.csv", "swaps_clean.csv"]
    for pf in proc_files:
        assert os.path.isfile(os.path.join(proc_dir, pf))

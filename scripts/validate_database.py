"""
Phase 2 Database Validation Script
Tests MySQL schema integrity, foreign keys, unique constraints, and check constraints.
"""
import subprocess
import sys

MYSQL_EXE = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

def run_sql(query, database="smart_coupon_swap"):
    cmd = [MYSQL_EXE, "-u", "root", "-e", query]
    if database:
        cmd.extend(["-D", database])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_suite():
    print("==================================================")
    print("PHASE 2 DATABASE SCHEMA INTEGRITY TEST SUITE")
    print("==================================================")
    
    passed = 0
    total = 0

    # Test 1: Verify tables exist
    total += 1
    rc, out, err = run_sql("SHOW TABLES;")
    expected_tables = {
        'roles', 'users', 'categories', 'brands', 'coupons',
        'user_category_preferences', 'user_brand_preferences', 'user_general_preferences',
        'coupon_views', 'coupon_requests', 'coupon_usage',
        'swaps', 'swap_items', 'swap_history',
        'ratings', 'reports', 'notifications'
    }
    found_tables = set(out.split())
    if expected_tables.issubset(found_tables):
        print(f"[PASS] Test 1: All {len(expected_tables)} required tables exist in smart_coupon_swap.")
        passed += 1
    else:
        print(f"[FAIL] Test 1: Missing tables: {expected_tables - found_tables}")

    # Test 2: Foreign key rejection on coupons (invalid user)
    total += 1
    bad_fk_sql = "INSERT INTO coupons (owner_id, category_id, brand_id, coupon_code_encrypted, title, discount_value, issue_date, expiry_date) VALUES (9999, 1, 1, 'ENC_123', 'Invalid Coupon', 10.00, '2026-09-01', '2026-10-01');"
    rc, out, err = run_sql(bad_fk_sql)
    if rc != 0 and "foreign key constraint fails" in err.lower():
        print("[PASS] Test 2: Foreign key correctly rejected non-existent owner_id (9999).")
        passed += 1
    else:
        print(f"[FAIL] Test 2: Expected FK error, got rc={rc}, err={err}")

    # Test 3: Unique constraint on user email
    total += 1
    dup_email_sql = "INSERT INTO users (role_id, name, email, password_hash) VALUES (2, 'Duplicate User', 'admin@smartswap.local', '$2b$12$DUMMY_HASH');"
    rc, out, err = run_sql(dup_email_sql)
    if rc != 0 and "duplicate entry" in err.lower():
        print("[PASS] Test 3: Unique constraint correctly rejected duplicate email.")
        passed += 1
    else:
        print(f"[FAIL] Test 3: Expected duplicate entry error, got rc={rc}, err={err}")

    # Test 4: Check constraint on discount_value > 0
    total += 1
    bad_discount_sql = "INSERT INTO coupons (owner_id, category_id, brand_id, coupon_code_encrypted, title, discount_value, issue_date, expiry_date) VALUES (2, 1, 1, 'ENC_ZERO', 'Zero Discount', 0.00, '2026-09-01', '2026-10-01');"
    rc, out, err = run_sql(bad_discount_sql)
    if rc != 0 and "check constraint" in err.lower():
        print("[PASS] Test 4: Check constraint correctly rejected discount_value <= 0.")
        passed += 1
    else:
        print(f"[FAIL] Test 4: Expected check constraint failure, got rc={rc}, err={err}")

    # Test 5: Check constraint on expiry_date >= issue_date
    total += 1
    bad_date_sql = "INSERT INTO coupons (owner_id, category_id, brand_id, coupon_code_encrypted, title, discount_value, issue_date, expiry_date) VALUES (2, 1, 1, 'ENC_DATE', 'Expired Issue', 50.00, '2026-10-01', '2026-09-01');"
    rc, out, err = run_sql(bad_date_sql)
    if rc != 0 and "check constraint" in err.lower():
        print("[PASS] Test 5: Check constraint correctly rejected expiry_date < issue_date.")
        passed += 1
    else:
        print(f"[FAIL] Test 5: Expected check constraint failure, got rc={rc}, err={err}")

    # Test 6: Check constraint on self-rating
    total += 1
    # First insert a valid coupon and swap for testing
    setup_sql = """
    INSERT INTO coupons (coupon_id, owner_id, category_id, brand_id, coupon_code_encrypted, title, discount_value, issue_date, expiry_date) 
    VALUES (101, 2, 1, 5, 'ENC_SWIGGY_50', 'Swiggy 50% Off', 50.00, '2026-09-01', '2026-12-31');
    INSERT INTO coupons (coupon_id, owner_id, category_id, brand_id, coupon_code_encrypted, title, discount_value, issue_date, expiry_date) 
    VALUES (102, 3, 2, 3, 'ENC_MYNTRA_30', 'Myntra 30% Off', 30.00, '2026-09-01', '2026-12-31');
    INSERT INTO swaps (swap_id, initiator_id, receiver_id, offered_coupon_id, requested_coupon_id, status)
    VALUES (501, 2, 3, 101, 102, 'COMPLETED');
    """
    run_sql(setup_sql)
    
    self_rate_sql = "INSERT INTO ratings (swap_id, rater_id, rated_user_id, score, review_text) VALUES (501, 2, 2, 5, 'Self rating test');"
    rc, out, err = run_sql(self_rate_sql)
    if rc != 0 and "check constraint" in err.lower():
        print("[PASS] Test 6: Check constraint correctly prevented user from rating themselves (rater_id = rated_user_id).")
        passed += 1
    else:
        print(f"[FAIL] Test 6: Expected check constraint failure, got rc={rc}, err={err}")

    # Test 7: Unique constraint on duplicate swap rating by same user
    total += 1
    valid_rate_sql = "INSERT INTO ratings (swap_id, rater_id, rated_user_id, score, review_text) VALUES (501, 2, 3, 5, 'Great swap!');"
    rc, out, err = run_sql(valid_rate_sql)
    # Now attempt duplicate
    dup_rate_sql = "INSERT INTO ratings (swap_id, rater_id, rated_user_id, score, review_text) VALUES (501, 2, 3, 4, 'Duplicate swap rating');"
    rc, out, err = run_sql(dup_rate_sql)
    if rc != 0 and "duplicate entry" in err.lower():
        print("[PASS] Test 7: Unique constraint correctly rejected duplicate rating on the same swap by the same user.")
        passed += 1
    else:
        print(f"[FAIL] Test 7: Expected duplicate rating rejection, got rc={rc}, err={err}")

    # Test 8: Clean re-execution of schema.sql and seed.sql
    total += 1
    recreate_sql = "DROP DATABASE IF EXISTS smart_coupon_swap; source database/schema.sql; source database/seed.sql;"
    rc, out, err = run_sql(recreate_sql, database=None)
    if rc == 0:
        print("[PASS] Test 8: Schema and seed cleanly dropped and recreated without warnings or errors.")
        passed += 1
    else:
        print(f"[FAIL] Test 8: Schema re-creation failed with rc={rc}, err={err}")

    print("==================================================")
    print(f"RESULTS: {passed}/{total} tests passed.")
    print("==================================================")
    return passed == total

if __name__ == "__main__":
    success = test_suite()
    sys.exit(0 if success else 1)

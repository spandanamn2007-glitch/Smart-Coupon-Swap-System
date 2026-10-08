"""
Database Connection & Query Helper Service
Smart Coupon Swap System

Provides MySQL connection management using PyMySQL with DictCursor.
Fallback logic ensures DB queries work cleanly both inside request contexts
and standalone test/script runners.
"""

import pymysql
import pymysql.cursors

def get_db_connection():
    """Establishes and returns a new MySQL database connection."""
    try:
        from flask import current_app
        config = current_app.config
        host = config["DB_HOST"]
        port = config["DB_PORT"]
        user = config["DB_USER"]
        password = config["DB_PASSWORD"]
        database = config["DB_NAME"]
    except (RuntimeError, KeyError, Exception):
        from app.config import Config
        host = Config.DB_HOST
        port = Config.DB_PORT
        user = Config.DB_USER
        password = Config.DB_PASSWORD
        database = Config.DB_NAME

    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4"
    )
    return connection

def execute_one(query, params=None):
    """Executes query and returns a single record dict or None."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
    finally:
        conn.close()

def execute_all(query, params=None):
    """Executes query and returns all matching records as a list of dicts."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
    finally:
        conn.close()

def execute_write(query, params=None):
    """Executes an INSERT/UPDATE/DELETE query and returns lastrowid and affected rows."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            return last_id, affected
    finally:
        conn.close()



def execute_transaction(steps):
    """
    Executes a list of (query, params) tuples atomically (autocommit=False).

    Returns a list of lastrowid values for each step.
    On any error, rolls back the entire transaction and re-raises.
    """
    import pymysql
    import pymysql.cursors

    try:
        from flask import current_app
        cfg = current_app.config
        host = cfg["DB_HOST"]
        port = cfg["DB_PORT"]
        user = cfg["DB_USER"]
        password = cfg["DB_PASSWORD"]
        database = cfg["DB_NAME"]
    except (RuntimeError, KeyError, Exception):
        from app.config import Config
        host = Config.DB_HOST
        port = Config.DB_PORT
        user = Config.DB_USER
        password = Config.DB_PASSWORD
        database = Config.DB_NAME

    conn = pymysql.connect(
        host=host, port=port, user=user, password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False, charset="utf8mb4"
    )
    try:
        last_ids = []
        with conn.cursor() as cursor:
            for sql, params in steps:
                cursor.execute(sql, params or ())
                last_ids.append(cursor.lastrowid)
        conn.commit()
        return last_ids
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

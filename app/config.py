"""
Flask Application Configuration
Smart Coupon Swap System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

_env = os.getenv("FLASK_ENV", "development")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_smart_coupon_swap_2026")

    # Database Settings (TiDB Cloud — MySQL-compatible, port 4000, TLS required)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 4000))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smart_coupon_swap")
    DB_SSL_REQUIRED = os.getenv("DB_SSL_REQUIRED", "true").strip().lower() in ("true", "1", "yes")

    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    # Use secure cookies in production (Vercel always serves HTTPS)
    SESSION_COOKIE_SECURE = _env == "production"

    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DB_NAME = os.getenv("DB_TEST_NAME", "smart_coupon_swap")
    SESSION_COOKIE_SECURE = False


"""
Smart Coupon Swap System — Application Entrypoint
-------------------------------------------------
Project: Smart Coupon Swap System
Phase: Phase 6 (Feature Engineering, Backend Foundation & Authentication)

Initializes and starts the Flask Web Server.
"""

from dotenv import load_dotenv
from app import create_app

load_dotenv()

app = create_app()

if __name__ == "__main__":
    print("==================================================")
    print("STARTING SMART COUPON SWAP SYSTEM FLASK BACKEND")
    print("Environment: Development")
    print("Port: 5000")
    print("==================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)

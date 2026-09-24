"""
WSGI Entrypoint — Smart Coupon Swap System
-------------------------------------------
This file is the Vercel deployment entrypoint.

Vercel's @vercel/python builder looks for a module-level `app` variable
(a WSGI callable) in well-known filenames. `wsgi.py` is explicitly supported.

This file does NOT duplicate any application logic.
It simply imports the existing Flask app from app/__init__.py via create_app().

Local development: use `python run.py` as before.
Vercel production:  Vercel calls `app` (this WSGI object) directly.
"""

import os
from dotenv import load_dotenv

# Load .env for local runs (no-op on Vercel where env vars come from the dashboard)
load_dotenv()

from app import create_app

# Vercel requires a module-level variable named `app` that is a WSGI callable.
app = create_app()

# Smart Coupon Swap System – Deployment Guide

## 1. Prerequisites
- **Operating System**: Linux (Ubuntu 22.04+ recommended) or Windows (WSL2) with Bash support.
- **Python**: 3.11 or newer (the project uses 3.13.7 locally). Install from <https://www.python.org/downloads/>.
- **MySQL**: version 8.x.
- **Git**: for cloning the repository.
- **Node.js (optional)**: only needed if you decide to add a SPA front‑end later.

## 2. Clone the Repository & Set Up a Virtual Environment
```bash
# Clone the repo (replace with your fork if you forked)
git clone https://github.com/spandanamn2007-glitch/Smart-Coupon-Swap-System.git
cd Smart-Coupon-Swap-System

# Create a virtual environment (recommended)
python -m venv .venv
# Activate (Linux/macOS)
source .venv/bin/activate
# Activate (Windows PowerShell)
.\\venv\\Scripts\\Activate.ps1
```

## 3. Install Python Dependencies
```bash
pip install -r requirements.txt
# Additional optional packages used by the dashboard (already in requirements)
# Flask, PyMySQL, Werkzeug, scikit-learn, joblib, networkx, pandas, numpy
```

## 4. Environment Variables (`.env`)
Create a file named `.env` in the project root with the following keys **(do NOT commit this file)**:
```
# Flask secret key – generate a strong random string (e.g. `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
SECRET_KEY="your-strong-secret"

# Flask environment (development or production)
FLASK_ENV=development   # change to "production" on live servers

# MySQL connection details
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=smart_coupon_swap
```
> **Important**: In production set `SESSION_COOKIE_SECURE=True` (see security‑audit below) and ensure `SECRET_KEY` is kept secret.

## 5. MySQL Setup
```sql
-- Log into MySQL as a privileged user
mysql -u root -p

-- Create the database (if not exists)
CREATE DATABASE IF NOT EXISTS smart_coupon_swap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_coupon_swap;

-- Run the schema script to create tables and seed required lookup data
SOURCE database/schema.sql;

-- Insert essential roles (admin = 1, user = 2)
INSERT INTO roles (role_id, role_name) VALUES (1, 'admin'), (2, 'user') ON DUPLICATE KEY UPDATE role_name=VALUES(role_name);
```
> The `schema.sql` file already defines all tables (users, coupons, swaps, notifications, etc.).

## 6. Train / Refresh Machine‑Learning Models (optional but recommended)
If you have processed feature data (`data/features/*.csv`), run the training script:
```bash
python scripts/train_models.py
```
This will generate three joblib model files under `models/` (these are **ignored** by Git via `.gitignore`).

## 7. Running the Application
### Development Server
```bash
# Export FLASK_APP if not already set
set FLASK_APP=run.py   # Windows PowerShell
export FLASK_APP=run.py   # Linux/macOS

# Run with debug mode (default from .env)
python run.py
```
The app will be available at <http://127.0.0.1:5000>.  The landing page (`/`) shows the login/register UI; after authentication you can access the dashboards at `/dashboard`, `/dashboard/analytics`, and `/dashboard/admin` (admin only).

### Production Server (Gunicorn + Nginx example)
```bash
# Install gunicorn in the virtualenv
pip install gunicorn

# Run 4 worker processes bound to 0.0.0.0:5000
gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
```
Typical production setup places Gunicorn behind an **NGINX** reverse proxy with TLS termination:
```nginx
server {
    listen 443 ssl;
    server_name your.domain.com;

    ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
> Ensure `SESSION_COOKIE_SECURE=True` in `app/config.py` (or via env) so cookies are only sent over HTTPS.

## 8. Health Check
```bash
curl http://localhost:5000/health
```
Expected JSON response:
```json
{"status": "ok", "timestamp": "2026-09-24T17:00:00Z"}
```
Use this endpoint for load‑balancer health probes.

## 9. Production Checklist (Security)
- Set `FLASK_ENV=production`.
- Use a **strong, random** `SECRET_KEY`.
- Enable `SESSION_COOKIE_SECURE=True`.
- Disable `DEBUG=True`.
- Serve via HTTPS (TLS termination in front‑end proxy).
- Review the **Security Audit** (see `docs/security-audit.md`).
- Apply database backups and enable binary logs for point‑in‑time recovery.
- Regularly rotate MySQL credentials and store them in a secrets manager.

## 10. Troubleshooting
| Symptom | Likely Cause | Fix |
|---|---|---|
| `ImportError: No module named …` | Missing dependencies | Run `pip install -r requirements.txt` |
| DB connection errors | Wrong `.env` values or MySQL not running | Verify `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` |
| 500 Internal Server Error after login | `SECRET_KEY` missing or empty | Ensure `.env` contains a non‑empty `SECRET_KEY` |
| Model loading errors (`FileNotFoundError`) | Models not trained | Run `python scripts/train_models.py` or copy pre‑trained `.joblib` files into `models/` |
| Static assets (CSS/JS) not loading | Flask not serving `static/` folder | Ensure `app/__init__.py` is using the default static folder (it does) |

---
*This guide assumes a fresh deployment. Adjust paths and environment variables to match your infrastructure.*

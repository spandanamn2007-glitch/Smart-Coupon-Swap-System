"""
Dashboard Routes
Smart Coupon Swap System

Serves HTML dashboard pages for users and admin.
"""

from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    """Landing page — show login/register if not authenticated."""
    if session.get("user_id"):
        return redirect(url_for("dashboard.user_dashboard"))
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
def user_dashboard():
    """User personal dashboard page."""
    if not session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return render_template("dashboard/user.html", user_id=session["user_id"])


@dashboard_bp.route("/dashboard/analytics")
def analytics_dashboard():
    """Data science and analytics dashboard page."""
    if not session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return render_template("dashboard/analytics.html")


@dashboard_bp.route("/dashboard/admin")
def admin_dashboard():
    """Admin system dashboard page — requires role_id=1."""
    if not session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if session.get("role_id") != 1:
        return render_template("dashboard/unauthorized.html"), 403
    return render_template("dashboard/admin.html")

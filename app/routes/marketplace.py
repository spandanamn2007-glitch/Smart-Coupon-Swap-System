"""
Marketplace Page Routes
Smart Coupon Swap System

Serves HTML pages for the coupon marketplace UI.
All routes redirect to login if session is missing.
"""

from flask import Blueprint, render_template, session, redirect, url_for

marketplace_bp = Blueprint("marketplace", __name__)


def _require_login():
    """Returns a redirect to login if user is not authenticated."""
    if not session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return None


@marketplace_bp.route("/marketplace")
def marketplace():
    """Marketplace — browse all available coupons."""
    redir = _require_login()
    if redir:
        return redir
    return render_template("marketplace.html")


@marketplace_bp.route("/coupons/add")
def add_coupon_page():
    """Add Coupon page — form to create a new coupon."""
    redir = _require_login()
    if redir:
        return redir
    return render_template("add_coupon.html")


@marketplace_bp.route("/my-coupons")
def my_coupons():
    """My Coupons — view/edit/delete the logged-in user's coupons."""
    redir = _require_login()
    if redir:
        return redir
    return render_template("my_coupons.html")

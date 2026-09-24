"""
Notification Routes
Smart Coupon Swap System

Exposes notification retrieval and management endpoints.
"""

from flask import Blueprint, request, jsonify, session
from app.utils.auth_decorator import login_required
from app.services.notification_service import (
    get_user_notifications, create_notification, mark_notification_read
)

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


@notifications_bp.route("", methods=["GET"])
@login_required
def list_notifications():
    """Retrieves notifications for the current authenticated user."""
    user_id = session.get("user_id")
    limit = int(request.args.get("limit", 20))
    notifs = get_user_notifications(user_id, limit=limit)
    return jsonify({"count": len(notifs), "notifications": notifs}), 200


@notifications_bp.route("", methods=["POST"])
@login_required
def send_notification():
    """Creates a new notification record."""
    data = request.get_json() or {}
    target_user_id = data.get("user_id") or session.get("user_id")
    title = data.get("title", "").strip()
    message = data.get("message", "").strip()
    notif_type = data.get("type", "SYSTEM")

    if not title or not message:
        return jsonify({"error": "Missing required fields: title, message"}), 400

    notif_id = create_notification(target_user_id, title, message, notif_type)
    return jsonify({"message": "Notification created", "notification_id": notif_id}), 201


@notifications_bp.route("/<int:notification_id>/read", methods=["PUT"])
@login_required
def mark_read(notification_id):
    """Marks a notification as read."""
    user_id = session.get("user_id")
    success = mark_notification_read(notification_id, user_id)
    if not success:
        return jsonify({"error": "Notification not found or access denied"}), 404
    return jsonify({"message": "Notification marked as read"}), 200

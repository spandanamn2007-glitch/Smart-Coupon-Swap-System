"""
Notification Service
Smart Coupon Swap System

Creates and retrieves notifications for system events:
recommendations, swap proposals, cycle matches, and expiry warnings.
"""

from app.services.db import execute_all, execute_one, execute_write


def create_notification(user_id, title, message, notif_type="SYSTEM"):
    """Inserts a notification record into the Phase 2 notifications table."""
    sql = """
        INSERT INTO notifications (user_id, title, message, type, is_read)
        VALUES (%s, %s, %s, %s, 0);
    """
    notif_id, _ = execute_write(sql, (user_id, title, message, notif_type))
    return notif_id


def get_user_notifications(user_id, limit=20):
    """Retrieves notifications for the specified user."""
    sql = """
        SELECT notification_id, user_id, title, message, type, is_read, created_at
        FROM notifications
        WHERE user_id = %s
        ORDER BY notification_id DESC
        LIMIT %s;
    """
    results = execute_all(sql, (user_id, limit))
    for r in results:
        r["is_read"] = bool(r["is_read"])
        r["created_at"] = str(r["created_at"])
    return results


def mark_notification_read(notification_id, user_id):
    """Marks a notification as read if owned by user."""
    sql = "UPDATE notifications SET is_read = 1 WHERE notification_id = %s AND user_id = %s;"
    _, affected = execute_write(sql, (notification_id, user_id))
    return affected > 0

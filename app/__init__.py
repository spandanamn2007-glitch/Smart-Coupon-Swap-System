"""
Application Factory
Smart Coupon Swap System
"""

from flask import Flask, jsonify
from app.config import Config
from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.users import users_bp
from app.routes.coupons import coupons_bp
from app.routes.recommendations import recommendations_bp
from app.routes.swaps import swaps_bp
from app.routes.predictions import predictions_bp
from app.routes.notifications import notifications_bp
from app.routes.dashboard import dashboard_bp
from app.routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Register Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(coupons_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(swaps_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "details": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized access"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden access"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app

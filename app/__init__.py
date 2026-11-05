from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database import close_db, init_db


def create_app(config_class=Config):
    """Flask application factory for PayPilot AI."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable Cross-Origin Resource Sharing (CORS) for frontend integration
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Teardown database connections
    app.teardown_appcontext(close_db)

    # Initialize database tables and seed data if not present
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            app.logger.warning(f"Database init check: {e}")

    # Register blueprints
    from app.routes.health_routes import health_bp
    from app.routes.catalogue_routes import catalogue_bp
    from app.routes.budget_guard_routes import budget_guard_bp
    from app.routes.bill_routes import bill_bp
    from app.routes.order_routes import order_bp
    from app.routes.ai_routes import ai_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(catalogue_bp)
    app.register_blueprint(budget_guard_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(ai_bp)

    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": "error",
            "message": "Bad request",
            "details": str(error)
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Endpoint not found"
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

    return app

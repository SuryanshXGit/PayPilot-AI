import os
from flask import Blueprint, jsonify, request, send_from_directory
from app.database import get_db

health_bp = Blueprint("health", __name__)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))


@health_bp.route("/", methods=["GET"])
def index():
    if "text/html" in request.headers.get("Accept", "") and os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return send_from_directory(FRONTEND_DIR, "index.html")
    return api_directory()


@health_bp.route("/api", methods=["GET"])
def api_directory():
    return jsonify({
        "name": "PayPilot AI Backend API",
        "version": "2.0.0",
        "description": "Budget-aware shopping and financial health backend for PayPal AI Hackathon",
        "docs_endpoints": {
            "health": "/api/health",
            "products": "/api/products",
            "categories": "/api/categories",
            "budget_guard_check": "POST /api/budget-guard/check",
            "budget_guard_optimize": "POST /api/budget-guard/optimize-bundle",
            "budget_guard_alternatives": "POST /api/budget-guard/alternatives",
            "bills": "/api/bills",
            "bills_summary": "/api/bills/summary",
            "order_prepare": "POST /api/orders/prepare",
            "order_verify_capture": "POST /api/orders/verify-capture",
            "ai_parse_intent": "POST /api/ai/parse-intent",
            "ai_recommend_bundle": "POST /api/ai/recommend-bundle",
            "ai_chat": "POST /api/ai/chat",
            "ai_voice_command": "POST /api/ai/voice-command",
            "ai_smart_filter": "POST /api/ai/smart-filter"
        }
    }), 200


@health_bp.route("/<path:filename>")
def serve_frontend_assets(filename):
    if os.path.exists(os.path.join(FRONTEND_DIR, filename)):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"status": "error", "message": f"Asset '{filename}' not found"}), 404


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint verifying database connectivity."""
    db_ok = False
    products_count = 0
    bills_count = 0
    try:
        db = get_db()
        cursor = db.execute("SELECT COUNT(*) as c FROM products")
        products_count = cursor.fetchone()["c"]
        cursor = db.execute("SELECT COUNT(*) as c FROM bills")
        bills_count = cursor.fetchone()["c"]
        db_ok = True
    except Exception as e:
        db_ok = False

    return jsonify({
        "status": "healthy" if db_ok else "unhealthy",
        "database": {
            "connected": db_ok,
            "catalogue_products_count": products_count,
            "bills_count": bills_count
        },
        "service": "PayPilot AI Flask Backend"
    }), 200 if db_ok else 500

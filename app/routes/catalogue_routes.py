from flask import Blueprint, request, jsonify
from app.services.catalogue_service import CatalogueService

catalogue_bp = Blueprint("catalogue", __name__, url_prefix="/api")


@catalogue_bp.route("/products", methods=["GET"])
def list_products():
    """
    Get all catalogue products with optional filters.
    Query parameters:
    - category (str)
    - search (str)
    - min_price (float)
    - max_price (float)
    - sort_by (str: 'price_asc', 'price_desc', 'reliability_desc')
    - in_stock_only (bool)
    """
    category = request.args.get("category")
    search = request.args.get("search")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort_by")
    in_stock_only = request.args.get("in_stock_only", default="false").lower() in ("true", "1")

    products = CatalogueService.get_all_products(
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        in_stock_only=in_stock_only
    )

    return jsonify({
        "status": "success",
        "count": len(products),
        "data_source_disclosure": "Controlled catalogue prices with verified retail benchmarks.",
        "products": [p.to_dict() for p in products]
    }), 200


@catalogue_bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """Retrieve details for a single catalogue item."""
    product = CatalogueService.get_product_by_id(product_id)
    if not product:
        return jsonify({
            "status": "error",
            "message": f"Product with ID '{product_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "product": product.to_dict()
    }), 200


@catalogue_bp.route("/products/<product_id>/price-history", methods=["GET"])
def get_product_price_history(product_id):
    """
    Retrieve price movement history for an item.
    Complies with hackathon guardrails: labels simulated Honey trend data.
    """
    history_data = CatalogueService.get_price_history(product_id)
    if not history_data:
        return jsonify({
            "status": "error",
            "message": f"Product with ID '{product_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "price_history": history_data
    }), 200


@catalogue_bp.route("/categories", methods=["GET"])
def list_categories():
    """Retrieve available categories with summary stats."""
    categories = CatalogueService.get_categories()
    return jsonify({
        "status": "success",
        "count": len(categories),
        "categories": categories
    }), 200

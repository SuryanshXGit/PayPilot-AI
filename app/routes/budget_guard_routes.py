from flask import Blueprint, request, jsonify
from app.services.budget_guard import BudgetGuardService

budget_guard_bp = Blueprint("budget_guard", __name__, url_prefix="/api/budget-guard")


@budget_guard_bp.route("/check", methods=["POST"])
def check_bundle():
    """
    Budget Guard deterministic budget verification.
    Payload:
    {
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00,
        "apply_tax": false,
        "apply_shipping": false,
        "include_bills": true,
        "bills_due_within_days": 7
    }
    """
    data = request.get_json() or {}
    item_ids = data.get("item_ids")
    stated_budget = data.get("stated_budget")

    if item_ids is None or stated_budget is None:
        return jsonify({
            "status": "error",
            "message": "Both 'item_ids' (list) and 'stated_budget' (number) are required."
        }), 400

    if not isinstance(item_ids, list):
        return jsonify({
            "status": "error",
            "message": "'item_ids' must be a list of product ID strings."
        }), 400

    try:
        stated_budget_float = float(stated_budget)
        if stated_budget_float < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "'stated_budget' must be a non-negative number."
        }), 400

    apply_tax = bool(data.get("apply_tax", False))
    apply_shipping = bool(data.get("apply_shipping", False))
    include_bills = bool(data.get("include_bills", False))
    bills_due_within_days = int(data.get("bills_due_within_days", 7))

    result = BudgetGuardService.check_bundle(
        item_ids=item_ids,
        stated_budget=stated_budget_float,
        apply_tax=apply_tax,
        apply_shipping=apply_shipping,
        include_bills=include_bills,
        bills_due_within_days=bills_due_within_days
    )

    return jsonify({
        "status": "success",
        "result": result
    }), 200


@budget_guard_bp.route("/optimize-bundle", methods=["POST"])
def optimize_bundle():
    """
    Multi-Item Budget Optimizer.
    Evaluates combinations across categories to maximize priority under budget.
    Payload:
    {
        "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
        "stated_budget": 150.00,
        "priority": "reliability"  // or "cost", "balanced"
    }
    """
    data = request.get_json() or {}
    categories = data.get("categories")
    stated_budget = data.get("stated_budget")

    if not categories or stated_budget is None:
        return jsonify({
            "status": "error",
            "message": "'categories' (list) and 'stated_budget' (number) are required."
        }), 400

    if not isinstance(categories, list) or len(categories) == 0:
        return jsonify({
            "status": "error",
            "message": "'categories' must be a non-empty list of category names."
        }), 400

    try:
        stated_budget_float = float(stated_budget)
        if stated_budget_float < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "'stated_budget' must be a non-negative number."
        }), 400

    priority = data.get("priority", "reliability")
    apply_tax = bool(data.get("apply_tax", False))
    apply_shipping = bool(data.get("apply_shipping", False))

    result = BudgetGuardService.optimize_bundle(
        categories=categories,
        stated_budget=stated_budget_float,
        priority=priority,
        apply_tax=apply_tax,
        apply_shipping=apply_shipping
    )

    if "error" in result:
        return jsonify({
            "status": "error",
            "message": result["error"]
        }), 404

    return jsonify({
        "status": "success",
        "result": result
    }), 200


@budget_guard_bp.route("/alternatives", methods=["POST"])
def suggest_alternatives():
    """
    Suggest swaps to bring an over-budget selection within budget.
    Payload:
    {
        "current_item_ids": ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00
    }
    """
    data = request.get_json() or {}
    current_item_ids = data.get("current_item_ids")
    stated_budget = data.get("stated_budget")

    if not current_item_ids or stated_budget is None:
        return jsonify({
            "status": "error",
            "message": "'current_item_ids' (list) and 'stated_budget' (number) are required."
        }), 400

    try:
        stated_budget_float = float(stated_budget)
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "'stated_budget' must be a valid number."
        }), 400

    apply_tax = bool(data.get("apply_tax", False))
    apply_shipping = bool(data.get("apply_shipping", False))

    result = BudgetGuardService.suggest_alternatives_for_over_budget(
        current_item_ids=current_item_ids,
        stated_budget=stated_budget_float,
        apply_tax=apply_tax,
        apply_shipping=apply_shipping
    )

    return jsonify({
        "status": "success",
        "result": result
    }), 200

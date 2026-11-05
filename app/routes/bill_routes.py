from flask import Blueprint, request, jsonify
from app.services.bill_service import BillService

bill_bp = Blueprint("bills", __name__, url_prefix="/api/bills")


@bill_bp.route("", methods=["GET"])
def list_bills():
    """
    List user bills with optional filtering.
    Query params:
    - due_within_days (int, e.g. 7)
    - is_paid (bool)
    - reference_date (str, YYYY-MM-DD)
    """
    due_within = request.args.get("due_within_days", type=int)
    is_paid_str = request.args.get("is_paid")
    is_paid = None
    if is_paid_str is not None:
        is_paid = is_paid_str.lower() in ("true", "1")
    reference_date_str = request.args.get("reference_date")

    bills = BillService.get_all_bills(
        due_within_days=due_within,
        is_paid=is_paid,
        reference_date_str=reference_date_str
    )

    return jsonify({
        "status": "success",
        "count": len(bills),
        "disclosure": "Deterministic bill reminders. Does not connect to or alter external bank accounts.",
        "bills": [b.to_dict() for b in bills]
    }), 200


@bill_bp.route("/<bill_id>", methods=["GET"])
def get_bill(bill_id):
    bill = BillService.get_bill_by_id(bill_id)
    if not bill:
        return jsonify({
            "status": "error",
            "message": f"Bill with ID '{bill_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "bill": bill.to_dict()
    }), 200


@bill_bp.route("", methods=["POST"])
def create_bill():
    data = request.get_json() or {}
    if not data.get("title") or data.get("amount") is None or not data.get("due_date"):
        return jsonify({
            "status": "error",
            "message": "Fields 'title', 'amount', and 'due_date' (YYYY-MM-DD) are required."
        }), 400

    try:
        float(data["amount"])
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "'amount' must be a valid number."
        }), 400

    new_bill = BillService.create_bill(data)
    return jsonify({
        "status": "success",
        "message": "Bill record created successfully.",
        "bill": new_bill.to_dict()
    }), 201


@bill_bp.route("/<bill_id>", methods=["PUT"])
def update_bill(bill_id):
    data = request.get_json() or {}
    updated = BillService.update_bill(bill_id, data)
    if not updated:
        return jsonify({
            "status": "error",
            "message": f"Bill with ID '{bill_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "message": "Bill updated successfully.",
        "bill": updated.to_dict()
    }), 200


@bill_bp.route("/<bill_id>", methods=["DELETE"])
def delete_bill(bill_id):
    deleted = BillService.delete_bill(bill_id)
    if not deleted:
        return jsonify({
            "status": "error",
            "message": f"Bill with ID '{bill_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "message": f"Bill '{bill_id}' deleted successfully."
    }), 200


@bill_bp.route("/summary", methods=["GET"])
def bills_summary():
    """
    Proactive Financial Health Summary.
    Computes upcoming bills due within 7 days and deductible impact on shopping budget.
    Query params:
    - shopping_budget (float)
    - days_window (int, default 7)
    - reference_date (str, YYYY-MM-DD)
    """
    shopping_budget = request.args.get("shopping_budget", type=float)
    days_window = request.args.get("days_window", default=7, type=int)
    reference_date_str = request.args.get("reference_date")

    summary = BillService.get_financial_health_summary(
        stated_shopping_budget=shopping_budget,
        days_window=days_window,
        reference_date_str=reference_date_str
    )

    return jsonify({
        "status": "success",
        "summary": summary
    }), 200

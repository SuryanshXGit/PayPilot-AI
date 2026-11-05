from flask import Blueprint, request, jsonify
from app.services.order_service import OrderService

order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.route("/prepare", methods=["POST"])
def prepare_order():
    data = request.get_json(silent=True) or {}
    item_ids = data.get("item_ids")
    stated_budget = data.get("stated_budget")
    apply_tax = bool(data.get("apply_tax", False))
    apply_shipping = bool(data.get("apply_shipping", False))

    if not item_ids or not isinstance(item_ids, list):
        return jsonify({
            "status": "error",
            "message": "'item_ids' must be a non-empty list of product IDs."
        }), 400

    try:
        order_data = OrderService.prepare_order(
            item_ids=item_ids,
            stated_budget=stated_budget,
            apply_tax=apply_tax,
            apply_shipping=apply_shipping
        )
        return jsonify({
            "status": "success",
            "order": order_data
        }), 201
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@order_bp.route("/<order_id>", methods=["GET"])
def get_order(order_id):
    """Fetch order details by order_id."""
    order = OrderService.get_order(order_id)
    if not order:
        return jsonify({
            "status": "error",
            "message": f"Order '{order_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "order": order
    }), 200


@order_bp.route("/<order_id>/create-paypal-order", methods=["POST"])
def create_paypal_order(order_id):
    """
    Create a PayPal Orders v2 record in PayPal Sandbox.
    Directs buyer to approval_url.
    Status transitions to PENDING_APPROVAL (never treated as paid).
    """
    data = request.get_json(silent=True) or {}
    return_url = data.get("return_url")
    cancel_url = data.get("cancel_url")

    try:
        res = OrderService.create_paypal_order(
            order_id=order_id,
            return_url=return_url,
            cancel_url=cancel_url
        )
        return jsonify({
            "status": "success",
            "paypal_order": res
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to initialize PayPal Sandbox checkout: {str(e)}"
        }), 502


@order_bp.route("/<order_id>/simulate-approval", methods=["POST"])
def simulate_approval(order_id):
    """
    Simulates the buyer approving the transaction at PayPal checkout.
    Transitions order to APPROVED state.
    Guarantees: Still NOT captured or confirmed paid until server captures and verifies.
    """
    try:
        res = OrderService.simulate_buyer_approval(order_id)
        return jsonify({
            "status": "success",
            "result": res
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@order_bp.route("/<order_id>/paypal-return", methods=["POST"])
def paypal_return(order_id):
    data = request.get_json(silent=True) or {}
    paypal_token = data.get("token")

    if not paypal_token:
        return jsonify({
            "status": "error",
            "message": "Missing PayPal order token."
        }), 400

    try:
        result = OrderService.confirm_paypal_approval(
            order_id=order_id,
            paypal_token=paypal_token
        )

        return jsonify({
            "status": "success",
            "result": result
        }), 200

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@order_bp.route("/<order_id>/capture", methods=["POST"])
def capture_order(order_id):
    """
    Server-side capture and verification of PayPal payment.
    Uses the PayPal order ID stored in the server database or passed in payload.
    """
    data = request.get_json(silent=True) or {}
    paypal_order_id = data.get("paypal_order_id")

    verification_result = OrderService.verify_and_capture_order(
        order_id=order_id,
        paypal_order_id=paypal_order_id
    )

    status_code = 200 if verification_result.get("verified") else 400

    return jsonify({
        "status": (
            "success"
            if verification_result.get("verified")
            else "error"
        ),
        "verification": verification_result
    }), status_code


@order_bp.route("/<order_id>/cancel", methods=["POST"])
def cancel_order(order_id):
    """
    Handles cancellation of PayPal checkout.
    Updates order status to CANCELLED and records reason.
    """
    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "Buyer cancelled checkout")

    try:
        res = OrderService.cancel_order(order_id, reason=reason)
        return jsonify({
            "status": "success",
            "order": res
        }), 200
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@order_bp.route("/<order_id>/pay-in-4", methods=["GET"])
def get_pay_in_4(order_id):
    """
    Provides estimated Pay in 4 installment breakdown with mandatory
    safety and affordability disclosures.
    """
    order = OrderService.get_order(order_id)
    if not order:
        return jsonify({
            "status": "error",
            "message": f"Order '{order_id}' not found."
        }), 404

    return jsonify({
        "status": "success",
        "order_id": order_id,
        "pay_in_4": order.get("pay_in_4_estimate")
    }), 200


@order_bp.route("/verify-capture", methods=["POST"])
def verify_capture():
    """
    Legacy / Client-side report capture verification endpoint.
    Ensures that the captured amount matches server-calculated totals.
    Payload:
    {
        "order_id": "PAYPILOT-...",
        "paypal_order_id": "8XY123456789...",
        "captured_amount": 137.97,
        "captured_currency": "USD"
    }
    """
    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    paypal_order_id = data.get("paypal_order_id")
    captured_amount = data.get("captured_amount")
    captured_currency = data.get("captured_currency", "USD")

    if not order_id or not paypal_order_id or captured_amount is None:
        return jsonify({
            "status": "error",
            "message": "'order_id', 'paypal_order_id', and 'captured_amount' are required."
        }), 400

    try:
        amount_float = float(captured_amount)
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "'captured_amount' must be a valid number."
        }), 400

    verification_result = OrderService.verify_and_capture_order(
        order_id=order_id,
        paypal_order_id=paypal_order_id,
        captured_amount=amount_float,
        captured_currency=captured_currency
    )

    status_code = 200 if verification_result.get("verified") else 400
    return jsonify({
        "status": "success" if verification_result.get("verified") else "error",
        "verification": verification_result
    }), status_code

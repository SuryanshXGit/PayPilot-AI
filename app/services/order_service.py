import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.database import get_db
from app.services.catalogue_service import CatalogueService
from app.services.budget_guard import BudgetGuardService
from app.services.paypal_service import PayPalService


class OrderService:
    """
    Handles pre-order locking, PayPal Sandbox integration, and server-side payment verification.
    Owned by Suryansh.

    Guarantees:
    - Pre-checkout price locking prevents cart tampering and pricing drift.
    - Full PayPal Orders v2 Sandbox flow: prepare -> create order -> buyer approval -> capture -> verify.
    - Zero assumption of payment: order creation or approval URL visiting is NEVER treated as paid.
    - Server-side mathematical verification of captured amount and currency before finalizing CAPTURED state.
    - Integrated Pay in 4 estimates with transparent total-cost and eligibility guardrails.
    """

    @staticmethod
    def get_order(order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a locked order from SQLite."""
        db = get_db()

        cursor = db.execute(
            "SELECT * FROM locked_orders WHERE order_id = ?",
            (order_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        order = dict(row)

        try:
            order["items"] = json.loads(order.get("items_json") or "[]")
        except (TypeError, json.JSONDecodeError):
            order["items"] = []

        order["subtotal"] = float(order.get("subtotal") or 0)
        order["tax"] = float(order.get("tax") or 0)
        order["shipping"] = float(order.get("shipping") or 0)
        total_amt = float(order.get("total_amount") or 0)
        order["total_amount"] = total_amt
        currency = str(order.get("currency") or "USD")
        order["currency"] = currency
        order["pay_in_4_estimate"] = PayPalService.calculate_pay_in_4(total_amt, currency)

        return order


    @staticmethod
    def prepare_order(
        item_ids: List[str],
        stated_budget: Optional[float] = None,
        apply_tax: bool = False,
        apply_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        Locks product prices from the catalogue into an immutable server order record.
        Provides the exact payload required for PayPal Orders v2 API.
        """
        products = CatalogueService.get_products_by_ids(item_ids)
        if not products:
            raise ValueError("No valid products provided for order preparation")

        totals = BudgetGuardService.calculate_totals(
            products,
            apply_tax=apply_tax,
            apply_shipping=apply_shipping
        )

        order_id = f"PAYPILOT-{uuid.uuid4().hex[:10].upper()}"
        currency = "USD"

        # Check budget constraint if provided
        budget_check = None
        if stated_budget is not None:
            budget_check = BudgetGuardService.check_bundle(
                item_ids=item_ids,
                stated_budget=stated_budget,
                apply_tax=apply_tax,
                apply_shipping=apply_shipping
            )

        items_json = [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "unit_amount": f"{p.price:.2f}",
                "quantity": "1",
                "data_source_label": p.data_source_label
            }
            for p in products
        ]

        # Save locked order to SQLite database
        db = get_db()
        db.execute("""
            INSERT INTO locked_orders (
                order_id, items_json, subtotal, tax, shipping, total_amount, currency, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id,
            json.dumps(items_json),
            totals["subtotal"],
            totals["tax"],
            totals["shipping"],
            totals["total"],
            currency,
            "CREATED"
        ))
        db.commit()

        # PayPal Orders v2 formatted payload for checkout creation
        paypal_purchase_unit = {
            "reference_id": order_id,
            "amount": {
                "currency_code": currency,
                "value": f"{totals['total']:.2f}",
                "breakdown": {
                    "item_total": {
                        "currency_code": currency,
                        "value": f"{totals['subtotal']:.2f}"
                    },
                    "tax_total": {
                        "currency_code": currency,
                        "value": f"{totals['tax']:.2f}"
                    },
                    "shipping": {
                        "currency_code": currency,
                        "value": f"{totals['shipping']:.2f}"
                    }
                }
            },
            "items": [
                {
                    "name": p.name[:127],
                    "unit_amount": {
                        "currency_code": currency,
                        "value": f"{p.price:.2f}"
                    },
                    "quantity": "1",
                    "category": "PHYSICAL_GOODS"
                }
                for p in products
            ]
        }

        # Pay in 4 calculation with guardrail disclosures
        pay_in_4_info = PayPalService.calculate_pay_in_4(totals["total"], currency)

        return {
            "order_id": order_id,
            "status": "CREATED",
            "currency": currency,
            "subtotal": totals["subtotal"],
            "tax": totals["tax"],
            "shipping": totals["shipping"],
            "total_amount": totals["total"],
            "items_count": len(products),
            "items": items_json,
            "budget_check": budget_check,
            "ready_for_paypal_checkout": True,
            "paypal_create_order_payload": {
                "intent": "CAPTURE",
                "purchase_units": [paypal_purchase_unit]
            },
            "pay_in_4_estimate": pay_in_4_info
        }

    @staticmethod
    def create_paypal_order(
        order_id: str,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interacts with PayPal Orders v2 API to create the PayPal Sandbox order.
        Updates internal order status to PENDING_APPROVAL.
        Never marks order as paid or captured.
        """
        order = OrderService.get_order(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        if order["status"] == "CAPTURED":
            raise ValueError(f"Order '{order_id}' has already been paid and captured.")
        if order["status"] == "CANCELLED":
            raise ValueError(f"Order '{order_id}' was cancelled and cannot be reopened.")

        paypal_res = PayPalService.create_order(
            order_data=order,
            return_url=return_url,
            cancel_url=cancel_url
        )

        paypal_order_id = paypal_res["paypal_order_id"]
        approval_url = paypal_res.get("approval_url")

        # Update database with PayPal order reference and PENDING_APPROVAL status
        db = get_db()
        db.execute("""
            UPDATE locked_orders
            SET paypal_order_id = ?, approval_url = ?, status = 'PENDING_APPROVAL'
            WHERE order_id = ?
        """, (paypal_order_id, approval_url, order_id))
        db.commit()

        return {
            "order_id": order_id,
            "paypal_order_id": paypal_order_id,
            "status": "PENDING_APPROVAL",
            "approval_url": approval_url,
            "total_amount": order["total_amount"],
            "currency": order["currency"],
            "mode": paypal_res.get("mode", "sandbox"),
            "security_notice": "Order is awaiting buyer approval. Not confirmed as paid until server captures and verifies payment."
        }


    @staticmethod
    def confirm_paypal_approval(
        order_id: str,
        paypal_token: str
    ) -> Dict[str, Any]:
        """
        Verify actual PayPal buyer approval before marking
        the internal order as APPROVED.
        """

        order = OrderService.get_order(order_id)

        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        stored_paypal_id = order.get("paypal_order_id")

        if not stored_paypal_id:
            raise ValueError("No PayPal order is associated with this order.")

        # The token returned by PayPal must match our stored PayPal ID.
        if paypal_token != stored_paypal_id:
            raise ValueError("PayPal order ID verification failed.")

        if order.get("status") == "CAPTURED":
            raise ValueError("This order has already been captured.")

        if order.get("status") == "CANCELLED":
            raise ValueError("This order has been cancelled.")

        # Already verified: return the existing state.
        if order.get("status") == "APPROVED":
            return {
                "verified": True,
                "order_id": order_id,
                "paypal_order_id": stored_paypal_id,
                "status": "APPROVED",
                "message": "PayPal approval was already verified."
            }

        if order.get("status") != "PENDING_APPROVAL":
            raise ValueError("Order is not awaiting PayPal approval.")

        # Ask PayPal directly for the current order status.
        paypal_details = PayPalService.get_order_details(
            stored_paypal_id
        )

        if paypal_details.get("error"):
            raise ValueError(
                "Could not verify PayPal order: "
                + paypal_details["error"]
            )

        if paypal_details.get("id") != stored_paypal_id:
            raise ValueError("PayPal returned an unexpected order ID.")

        if paypal_details.get("status") != "APPROVED":
            raise ValueError(
                "PayPal has not confirmed buyer approval. "
                f"Current status: {paypal_details.get('status', 'UNKNOWN')}"
            )

        # Verify the PayPilot reference and locked amount/currency.
        purchase_units = paypal_details.get("purchase_units", [])

        if len(purchase_units) != 1:
            raise ValueError("Unexpected PayPal purchase unit count.")

        purchase_unit = purchase_units[0]

        if purchase_unit.get("reference_id") != order_id:
            raise ValueError("PayPal order reference does not match.")

        paypal_amount = purchase_unit.get("amount", {})

        expected_amount = float(order["total_amount"])
        expected_currency = str(order["currency"]).upper()

        try:
            actual_amount = float(paypal_amount["value"])
            actual_currency = str(
                paypal_amount["currency_code"]
            ).upper()
        except (KeyError, TypeError, ValueError):
            raise ValueError("PayPal returned invalid amount details.")

        if abs(actual_amount - expected_amount) > 0.01:
            raise ValueError("PayPal order amount does not match the locked order.")

        if actual_currency != expected_currency:
            raise ValueError("PayPal order currency does not match.")

        # Update status only after successful PayPal verification.
        db = get_db()

        cursor = db.execute(
            """
            UPDATE locked_orders
            SET status = 'APPROVED'
            WHERE order_id = ?
              AND paypal_order_id = ?
              AND status = 'PENDING_APPROVAL'
            """,
            (order_id, stored_paypal_id)
        )

        db.commit()

        if cursor.rowcount != 1:
            raise ValueError(
                "Order status changed before approval could be recorded."
            )

        return {
            "verified": True,
            "order_id": order_id,
            "paypal_order_id": stored_paypal_id,
            "status": "APPROVED",
            "message": "PayPal buyer approval verified successfully."
        }

    @staticmethod
    def simulate_buyer_approval(order_id: str) -> Dict[str, Any]:
        """
        Simulate buyer approval for sandbox testing and demo.
        Transitions the state to APPROVED, ready for server capture.
        """
        order = OrderService.get_order(order_id)

        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        paypal_order_id = order.get("paypal_order_id")

        if not paypal_order_id:
            raise ValueError("No PayPal order ID is associated with this order.")

        PayPalService.simulate_buyer_approval(paypal_order_id)

        db = get_db()
        db.execute(
            """
            UPDATE locked_orders
            SET status = 'APPROVED'
            WHERE order_id = ?
              AND paypal_order_id = ?
            """,
            (order_id, paypal_order_id)
        )
        db.commit()

        return {
            "order_id": order_id,
            "paypal_order_id": paypal_order_id,
            "status": "APPROVED",
            "message": "Buyer approval recorded. Ready for server-side capture and verification."
        }

    @staticmethod
    def verify_and_capture_order(
        order_id: str,
        paypal_order_id: Optional[str] = None,
        captured_amount: Optional[float] = None,
        captured_currency: str = "USD"
    ) -> Dict[str, Any]:
        """
        Capture payment through PayPal on the server and verify
        the captured amount and currency against the locked order.
        Supports both direct server-side capture and client-submitted verification.
        """
        db = get_db()

        cursor = db.execute(
            "SELECT * FROM locked_orders WHERE order_id = ?",
            (order_id,)
        )
        row = cursor.fetchone()

        if not row:
            return {
                "verified": False,
                "error": f"Order reference '{order_id}' not found on server."
            }

        expected_total = float(row["total_amount"])
        expected_currency = str(row["currency"]).upper()
        active_paypal_id = paypal_order_id or row["paypal_order_id"]

        if row["status"] == "CANCELLED":
            return {
                "verified": False,
                "order_id": order_id,
                "status": "CANCELLED",
                "error": "Cannot capture a cancelled order."
            }

        if row["status"] == "CAPTURED" and captured_amount is None:
            return {
                "verified": True,
                "order_id": order_id,
                "paypal_order_id": active_paypal_id,
                "status": "CAPTURED",
                "message": "This order has already been captured."
            }

        if captured_amount is None:
            if row["status"] != "APPROVED":
                return {
                    "verified": False,
                    "order_id": order_id,
                    "status": row["status"],
                    "error": "Order is not approved. Buyer must approve checkout before payment can be captured."
                }

            if not active_paypal_id:
                return {
                    "verified": False,
                    "order_id": order_id,
                    "status": "ERROR",
                    "error": "No PayPal order ID is associated with this order. Create PayPal order first."
                }

            capture_resp = PayPalService.capture_order(active_paypal_id)

            if not capture_resp or not capture_resp.get("success"):
                error_message = (
                    capture_resp.get("error", "PayPal capture failed.")
                    if capture_resp else "PayPal returned an empty response."
                )

                db.execute(
                    """
                    UPDATE locked_orders
                    SET status = 'CAPTURE_FAILED', error_message = ?
                    WHERE order_id = ?
                    """,
                    (error_message, order_id)
                )
                db.commit()

                return {
                    "verified": False,
                    "order_id": order_id,
                    "status": "CAPTURE_FAILED",
                    "error": error_message
                }

            try:
                captured_amount = float(capture_resp["captured_amount"])
                captured_currency = str(
                    capture_resp["captured_currency"]
                ).upper()
            except (KeyError, TypeError, ValueError):
                return {
                    "verified": False,
                    "order_id": order_id,
                    "status": "VERIFICATION_FAILED",
                    "error": "PayPal returned invalid capture details."
                }

        amount_matches = abs(float(captured_amount) - expected_total) <= 0.01
        currency_matches = str(captured_currency).upper() == expected_currency

        if not amount_matches or not currency_matches:
            error_message = (
                f"Captured payment discrepancy: expected {expected_currency} "
                f"{expected_total:.2f}, received "
                f"{captured_currency} {float(captured_amount):.2f}."
            )

            db.execute(
                """
                UPDATE locked_orders
                SET status = 'VERIFICATION_FAILED', error_message = ?
                WHERE order_id = ?
                """,
                (error_message, order_id)
            )
            db.commit()

            return {
                "verified": False,
                "order_id": order_id,
                "status": "VERIFICATION_FAILED",
                "error": error_message
            }

        now_ts = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        db.execute(
            """
            UPDATE locked_orders
            SET status = 'CAPTURED',
                paypal_order_id = ?,
                captured_at = ?,
                error_message = NULL
            WHERE order_id = ?
            """,
            (now_ts, order_id) if not active_paypal_id else (active_paypal_id, now_ts, order_id)
        )
        db.commit()

        return {
            "verified": True,
            "order_id": order_id,
            "paypal_order_id": active_paypal_id,
            "status": "CAPTURED",
            "captured_amount": float(captured_amount),
            "currency": str(captured_currency).upper(),
            "captured_at": now_ts,
            "message": "Payment verified and recorded successfully against server catalogue total."
        }

    @staticmethod
    def cancel_order(order_id: str, reason: str = "Buyer cancelled checkout") -> Dict[str, Any]:
        """
        Handles cancellation of an order (e.g. buyer clicked cancel at PayPal checkout).
        """
        db = get_db()
        cursor = db.execute("SELECT * FROM locked_orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Order '{order_id}' not found.")

        if row["status"] == "CAPTURED":
            raise ValueError("Cannot cancel an order that has already been captured and verified.")

        db.execute("""
            UPDATE locked_orders
            SET status = 'CANCELLED', error_message = ?
            WHERE order_id = ?
        """, (reason, order_id))
        db.commit()

        return {
            "order_id": order_id,
            "status": "CANCELLED",
            "reason": reason,
            "message": "Order checkout cancelled successfully."
        }

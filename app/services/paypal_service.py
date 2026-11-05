import os
import json
import uuid
import base64
import time
from typing import Dict, Any, Optional
from flask import current_app


class PayPalService:
    """
    PayPal Sandbox Integration & Security Service.
    Owned by Suryansh.

    Responsibilities:
    - PayPal Sandbox Orders v2 API client (Create -> Approve -> Capture -> Verify).
    - Strict server-side verification: amount, currency, and capture state.
    - Zero assumption of payment prior to verified capture.
    - Pay in 4 calculation with mandatory affordability & eligibility disclaimers.
    - Seamless live Sandbox API support + robust deterministic simulation for offline/testing.
    """

    _token_cache: Dict[str, Any] = {}
    _simulated_orders: Dict[str, Any] = {}

    @classmethod
    def get_config(cls) -> Dict[str, str]:
        """Extract PayPal configuration with fallbacks."""
        if current_app:
            cfg = current_app.config
            return {
                "client_id": cfg.get("PAYPAL_CLIENT_ID", os.getenv("PAYPAL_CLIENT_ID", "")),
                "client_secret": cfg.get("PAYPAL_CLIENT_SECRET", os.getenv("PAYPAL_CLIENT_SECRET", "")),
                "env": cfg.get("PAYPAL_ENV", os.getenv("PAYPAL_ENV", "sandbox")),
                "api_base": cfg.get("PAYPAL_API_BASE", os.getenv("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com")),
                "return_url": cfg.get("PAYPAL_RETURN_URL", os.getenv("PAYPAL_RETURN_URL", "http://localhost:3000/checkout/success")),
                "cancel_url": cfg.get("PAYPAL_CANCEL_URL", os.getenv("PAYPAL_CANCEL_URL", "http://localhost:3000/checkout/cancel")),
            }
        return {
            "client_id": os.getenv("PAYPAL_CLIENT_ID", ""),
            "client_secret": os.getenv("PAYPAL_CLIENT_SECRET", ""),
            "env": os.getenv("PAYPAL_ENV", "sandbox"),
            "api_base": os.getenv("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com"),
            "return_url": os.getenv("PAYPAL_RETURN_URL", "http://localhost:3000/checkout/success"),
            "cancel_url": os.getenv("PAYPAL_CANCEL_URL", "http://localhost:3000/checkout/cancel"),
        }

    @classmethod
    def is_live_credentials_configured(cls) -> bool:
        """Check if real (non-placeholder) PayPal Sandbox credentials are provided."""
        if current_app and current_app.config.get("TESTING"):
            return False

        cfg = cls.get_config()
        client_id = cfg["client_id"].strip()
        client_secret = cfg["client_secret"].strip()

        is_placeholder = (
            not client_id or
            not client_secret or
            "your_paypal_sandbox" in client_id.lower() or
            "your_paypal_sandbox" in client_secret.lower() or
            client_id == "placeholder"
        )
        return not is_placeholder

    @classmethod
    def get_access_token(cls) -> str:
        """
        Retrieve OAuth2 Bearer token from PayPal.
        In live sandbox mode, queries /v1/oauth2/token with Basic Auth.
        In simulation mode, produces a mock sandbox token.
        """
        cfg = cls.get_config()
        if not cls.is_live_credentials_configured():
            return "SANDBOX_MOCK_BEARER_TOKEN_PAYPILOT"

        # Check cache
        now = time.time()
        cached = cls._token_cache.get("token")
        expires_at = cls._token_cache.get("expires_at", 0)
        if cached and now < (expires_at - 60):
            return cached

        import urllib.request
        import urllib.parse

        url = f"{cfg['api_base']}/v1/oauth2/token"
        credentials = f"{cfg['client_id']}:{cfg['client_secret']}"
        encoded_cred = base64.b64encode(credentials.encode()).decode("utf-8")

        headers = {
            "Authorization": f"Basic {encoded_cred}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
                token = body.get("access_token")
                expires_in = body.get("expires_in", 32400)
                cls._token_cache["token"] = token
                cls._token_cache["expires_at"] = now + expires_in
                return token
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with PayPal Sandbox: {e}")

    @classmethod
    def create_order(
        cls,
        order_data: Dict[str, Any],
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a PayPal Orders v2 record.
        - Sets intent to CAPTURE.
        - Enforces locked catalogue amount and breakdown.
        - Returns PayPal Order ID and buyer approval URL.
        """
        cfg = cls.get_config()
        ret_url = return_url or cfg["return_url"]
        can_url = cancel_url or cfg["cancel_url"]

        order_id = order_data["order_id"]
        currency = order_data.get("currency", "USD")
        total_amount = float(order_data["total_amount"])
        subtotal = float(order_data.get("subtotal", total_amount))
        tax = float(order_data.get("tax", 0.0))
        shipping = float(order_data.get("shipping", 0.0))

        items = order_data.get("items", [])
        purchase_items = []
        for itm in items:
            unit_val = float(itm.get("unit_amount", itm.get("price", total_amount)))
            qty = str(itm.get("quantity", "1"))
            purchase_items.append({
                "name": itm.get("name", "Product")[:127],
                "unit_amount": {
                    "currency_code": currency,
                    "value": f"{unit_val:.2f}"
                },
                "quantity": qty,
                "category": "PHYSICAL_GOODS"
            })

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": order_id,
                    "description": f"PayPilot AI Budget-Locked Purchase ({order_id})",
                    "amount": {
                        "currency_code": currency,
                        "value": f"{total_amount:.2f}",
                        "breakdown": {
                            "item_total": {
                                "currency_code": currency,
                                "value": f"{subtotal:.2f}"
                            },
                            "tax_total": {
                                "currency_code": currency,
                                "value": f"{tax:.2f}"
                            },
                            "shipping": {
                                "currency_code": currency,
                                "value": f"{shipping:.2f}"
                            }
                        }
                    },
                    "items": purchase_items
                }
            ],
            "application_context": {
                "brand_name": "PayPilot AI",
                "landing_page": "NO_PREFERENCE",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
                "return_url": ret_url,
                "cancel_url": can_url
            }
        }

        if cls.is_live_credentials_configured():
            import urllib.request

            token = cls.get_access_token()
            url = f"{cfg['api_base']}/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    paypal_id = res_body["id"]
                    approve_link = next(
                        (lnk["href"] for lnk in res_body.get("links", []) if lnk.get("rel") == "approve"),
                        None
                    )
                    return {
                        "paypal_order_id": paypal_id,
                        "status": res_body.get("status", "CREATED"),
                        "approval_url": approve_link,
                        "mode": "live_sandbox",
                        "raw_response": res_body
                    }
            except Exception as e:
                raise RuntimeError(f"PayPal Sandbox create order error: {e}")

        # Deterministic Sandbox Simulation mode
        paypal_id = f"SANDBOX-{uuid.uuid4().hex[:12].upper()}"
        approve_link = f"https://www.sandbox.paypal.com/checkoutnow?token={paypal_id}"

        simulated_data = {
            "id": paypal_id,
            "reference_id": order_id,
            "status": "CREATED",
            "amount": total_amount,
            "currency": currency,
            "payload": payload,
            "buyer_approved": False,
            "captured": False,
            "created_at": time.time(),
            "links": [
                {"rel": "self", "href": f"{cfg['api_base']}/v2/checkout/orders/{paypal_id}", "method": "GET"},
                {"rel": "approve", "href": approve_link, "method": "GET"},
                {"rel": "capture", "href": f"{cfg['api_base']}/v2/checkout/orders/{paypal_id}/capture", "method": "POST"}
            ]
        }
        cls._simulated_orders[paypal_id] = simulated_data

        return {
            "paypal_order_id": paypal_id,
            "status": "CREATED",
            "approval_url": approve_link,
            "mode": "simulated_sandbox",
            "message": "PayPal Sandbox order created. Direct buyer to approval_url to review and confirm."
        }

    @classmethod
    def simulate_buyer_approval(cls, paypal_order_id: str) -> Dict[str, Any]:
        """
        Simulates the buyer approving the order on the PayPal approval page.
        Transitions the PayPal Sandbox order to APPROVED state.
        NOTE: Order is still NOT captured and NOT paid until server captures and verifies.
        """
        if paypal_order_id in cls._simulated_orders:
            cls._simulated_orders[paypal_order_id]["buyer_approved"] = True
            cls._simulated_orders[paypal_order_id]["status"] = "APPROVED"
            return {
                "paypal_order_id": paypal_order_id,
                "status": "APPROVED",
                "message": "Buyer approved order on PayPal. Ready for server capture."
            }
        return {
            "paypal_order_id": paypal_order_id,
            "status": "APPROVED",
            "message": "Buyer approval recorded for live/external PayPal order."
        }


    @classmethod
    def capture_order(cls, paypal_order_id: str) -> Dict[str, Any]:
        """
        Capture a buyer-approved PayPal order.

        A real payment is successful only when PayPal confirms
        both the order and its capture as COMPLETED.
        """
        cfg = cls.get_config()

        if cls.is_live_credentials_configured():
            import urllib.request

            try:
                token = cls.get_access_token()

                url = (
                    f"{cfg['api_base']}/v2/checkout/orders/"
                    f"{paypal_order_id}/capture"
                )

                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }

                req = urllib.request.Request(
                    url,
                    data=b"{}",
                    headers=headers,
                    method="POST"
                )

                with urllib.request.urlopen(req, timeout=15) as response:
                    res_body = json.loads(
                        response.read().decode("utf-8")
                    )

                order_status = res_body.get("status", "")

                if order_status != "COMPLETED":
                    return {
                        "success": False,
                        "status": order_status or "UNKNOWN",
                        "error": (
                            "PayPal has not confirmed the order "
                            "as COMPLETED."
                        )
                    }

                captures = []

                for purchase_unit in res_body.get("purchase_units", []):
                    payments = purchase_unit.get("payments", {})
                    for capture in payments.get("captures", []):
                        captures.append(capture)

                if not captures:
                    return {
                        "success": False,
                        "status": "CAPTURE_NOT_FOUND",
                        "error": "PayPal returned no capture records."
                    }

                completed_captures = [
                    capture for capture in captures
                    if capture.get("status") == "COMPLETED"
                ]

                if not completed_captures:
                    return {
                        "success": False,
                        "status": "CAPTURE_NOT_COMPLETED",
                        "error": (
                            "PayPal did not confirm any capture "
                            "as COMPLETED."
                        )
                    }

                if len(completed_captures) != 1:
                    return {
                        "success": False,
                        "status": "UNEXPECTED_CAPTURE_COUNT",
                        "error": (
                            "Expected exactly one completed capture "
                            "for this order."
                        )
                    }

                first_capture = completed_captures[0]
                amount = first_capture.get("amount", {})

                if not amount.get("value") or not amount.get("currency_code"):
                    return {
                        "success": False,
                        "status": "INVALID_CAPTURE_DETAILS",
                        "error": "PayPal returned incomplete capture details."
                    }

                return {
                    "success": True,
                    "status": "COMPLETED",
                    "capture_id": first_capture.get("id"),
                    "captured_amount": float(amount["value"]),
                    "captured_currency": amount["currency_code"],
                    "raw_response": res_body
                }

            except Exception as e:
                return {
                    "success": False,
                    "status": "CAPTURE_FAILED",
                    "error": str(e)
                }

        # Simulation mode: this is a demo, not a real PayPal payment.
        order = cls._simulated_orders.get(paypal_order_id)

        if not order:
            return {
                "success": False,
                "status": "ORDER_NOT_FOUND",
                "error": (
                    f"Simulated PayPal order '{paypal_order_id}' "
                    "not found."
                )
            }

        if not order.get("buyer_approved"):
            return {
                "success": False,
                "status": "UNAPPROVED_PAYMENT",
                "error": (
                    "Cannot capture: Buyer has not approved "
                    "this PayPal order."
                )
            }

        if order.get("captured"):
            return {
                "success": False,
                "status": "ALREADY_CAPTURED",
                "error": "This simulated order has already been captured."
            }

        order["captured"] = True
        order["status"] = "COMPLETED"

        capture_id = f"CAP-{uuid.uuid4().hex[:10].upper()}"

        return {
            "success": True,
            "status": "COMPLETED",
            "capture_id": capture_id,
            "captured_amount": order["amount"],
            "captured_currency": order["currency"],
            "message": "Simulated payment completed successfully."
        }

    @classmethod
    def get_order_details(cls, paypal_order_id: str) -> Dict[str, Any]:
        """Fetch current order details from PayPal Orders v2."""
        cfg = cls.get_config()
        if cls.is_live_credentials_configured():
            import urllib.request

            token = cls.get_access_token()
            url = f"{cfg['api_base']}/v2/checkout/orders/{paypal_order_id}"
            headers = {"Authorization": f"Bearer {token}"}
            req = urllib.request.Request(url, headers=headers, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))
            except Exception as e:
                return {"error": str(e)}

        order = cls._simulated_orders.get(paypal_order_id)
        if not order:
            return {"status": "NOT_FOUND"}
        return {
            "id": order["id"],
            "status": order["status"],
            "amount": order["amount"],
            "currency": order["currency"],
            "buyer_approved": order["buyer_approved"],
            "captured": order["captured"]
        }

    @staticmethod
    def calculate_pay_in_4(total_amount: float, currency: str = "USD") -> Dict[str, Any]:
        """
        Computes Pay in 4 installment breakdown with mandatory hackathon safety disclaimers.
        Guardrails:
        - Must not treat installment as proof of affordability.
        - Must disclose that Pay in 4 is subject to PayPal credit approval and eligibility.
        - Must prominently show the full total cost.
        """
        # Standard US PayPal Pay in 4 thresholds: $30 to $1,500 USD
        MIN_PAY_IN_4 = 30.00
        MAX_PAY_IN_4 = 1500.00

        is_eligible_range = (MIN_PAY_IN_4 <= total_amount <= MAX_PAY_IN_4) and currency.upper() == "USD"

        base_installment = round(total_amount / 4.0, 2)
        # Adjust for rounding remainder on the final payment
        remainder = round(total_amount - (base_installment * 3), 2)

        return {
            "eligible_for_estimate": is_eligible_range,
            "total_purchase_amount": round(total_amount, 2),
            "currency": currency,
            "installment_count": 4 if is_eligible_range else 0,
            "installment_amount": base_installment if is_eligible_range else None,
            "final_installment_amount": remainder if is_eligible_range else None,
            "frequency": "Bi-weekly (every 2 weeks)" if is_eligible_range else None,
            "interest_rate": "0% APR",
            "payment_schedule": [
                {"payment_number": 1, "due": "Due today at checkout", "amount": base_installment},
                {"payment_number": 2, "due": "2 weeks from today", "amount": base_installment},
                {"payment_number": 3, "due": "4 weeks from today", "amount": base_installment},
                {"payment_number": 4, "due": "6 weeks from today", "amount": remainder}
            ] if is_eligible_range else [],
            "affordability_warning": (
                f"Important: Paying in 4 installments of ${base_installment:.2f} does not reduce your total financial obligation. "
                f"The full cost of this purchase remains ${total_amount:.2f}."
            ),
            "eligibility_disclaimer": (
                "PayPal Pay in 4 is subject to consumer eligibility and credit checks by PayPal at checkout. "
                "Availability depends on account standing, geography, and merchant qualification. It is not guaranteed."
            )
        }

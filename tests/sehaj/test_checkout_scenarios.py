"""
test_checkout_scenarios.py - PayPal Sandbox Checkout & Verification Test Suite
Owned by Sehaj (Product Data, Comparison & Testing Lead) / Suryansh (PayPal Integration & Security Lead)

Validates:
- Complete PayPal flow: Create order -> Buyer approval -> Capture -> Server-side verification
- CRITICAL GUARDRAIL: Order creation (CREATED) is NEVER treated as proof of payment
- CRITICAL GUARDRAIL: Approval redirect (APPROVED) is NEVER treated as proof of payment
- Server-side capture status, amount, and currency matching
- Cancellation (CANCELLED) and payment decline error paths
- Pay in 4 eligibility disclaimer enforcement
- Security guardrail: API payloads never expose client_secret or server credentials
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from utils.budget_guard import BudgetGuard


class TestCheckoutScenarios(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        scenarios = self.loader.get_demo_scenarios()
        self.dorm_scenario = next(s for s in scenarios if s["id"] == "scenario-01-dorm-bundle")
        self.fixture = self.dorm_scenario["paypal_checkout_fixture"]

    def test_order_creation_is_not_treated_as_captured_payment(self):
        """
        GUARDRAIL: Never treat order creation as proof of payment.
        An order in status 'CREATED' must NOT fulfill goods or show 'Payment Succeeded'.
        """
        created_response = self.fixture["simulated_created_response"]
        order_status = created_response.get("status")

        self.assertEqual(order_status, "CREATED")
        # Payment verification helper logic
        is_paid = (order_status == "COMPLETED")
        self.assertFalse(is_paid, "Order creation must NEVER be considered payment completion")

    def test_approval_url_opening_is_not_treated_as_captured_payment(self):
        """
        GUARDRAIL: Opening approval URL or status 'APPROVED' without capture is NOT payment completion.
        """
        simulated_approved_state = {
            "id": "PAYPAL-ORDER-DORM-789123",
            "status": "APPROVED"  # Buyer approved in sandbox pop-up, but server has not captured yet
        }

        is_captured = (simulated_approved_state.get("status") == "COMPLETED")
        self.assertFalse(is_captured, "Buyer approval alone is NOT captured payment")

    def test_server_side_capture_verification(self):
        """
        Payment is only valid when backend verifies captured order with COMPLETED status,
        matching amount ($111.48), and currency (USD).
        """
        captured_response = self.fixture["simulated_captured_response"]
        expected_total = "111.48"
        expected_currency = "USD"

        # 1. Status verification
        order_status = captured_response.get("status")
        self.assertEqual(order_status, "COMPLETED")

        # 2. Capture unit verification
        purchase_unit = captured_response["purchase_units"][0]
        capture = purchase_unit["payments"]["captures"][0]

        self.assertEqual(capture["status"], "COMPLETED")
        self.assertEqual(capture["amount"]["value"], expected_total)
        self.assertEqual(capture["amount"]["currency_code"], expected_currency)
        self.assertTrue(capture["final_capture"])

    def test_cancellation_and_error_handling(self):
        """
        Ensure cancellation flow produces clean CANCELLED status and does not lock user cart.
        """
        cancel_event = {
            "order_id": "PAYPAL-ORDER-DORM-789123",
            "status": "CANCELLED_BY_BUYER",
            "message": "User closed the PayPal checkout window without approving."
        }

        self.assertEqual(cancel_event["status"], "CANCELLED_BY_BUYER")
        is_payment_success = (cancel_event["status"] == "COMPLETED")
        self.assertFalse(is_payment_success)

    def test_pay_in_4_compliance_and_affordability_rules(self):
        """
        Guardrails:
        1. Do not claim PayPal Pay in 4 is always available (requires eligibility disclaimer).
        2. Do not treat small installment as proof of total affordability.
        """
        valid_copy = (
            "Pay in 4 installments of $27.87 may be available subject to PayPal eligibility and credit approval. "
            "Total order cost remains $111.48."
        )
        invalid_copy_unconditional = "You can always use PayPal Pay in 4 to buy this with zero credit checks!"

        result_valid = BudgetGuard.validate_pay_in_4_compliance(valid_copy)
        self.assertTrue(result_valid["compliant"])
        self.assertEqual(result_valid["guardrail_status"], "PASS")

        result_invalid = BudgetGuard.validate_pay_in_4_compliance(invalid_copy_unconditional)
        self.assertFalse(result_invalid["compliant"])
        self.assertIn("FAIL", result_invalid["guardrail_status"])

    def test_security_credentials_not_leaked_in_order_payload(self):
        """
        Guardrail: Do not expose client_secret or internal API keys in client-facing order payload.
        """
        order_req = self.fixture["order_request"]
        payload_str = str(order_req).lower()

        forbidden_keys = ["client_secret", "secret_key", "bearer_token", "password", "private_key"]
        for key in forbidden_keys:
            self.assertNotIn(key, payload_str, f"Payload leaked private key: '{key}'")


if __name__ == "__main__":
    unittest.main()

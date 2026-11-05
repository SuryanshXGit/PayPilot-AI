"""
PayPilot AI 2.0 — PayPal Sandbox Integration & Security Demo
Owner: Suryansh (PayPal Integration & Security)

Demonstrates:
1. College Dorm Bundle ($150 Budget):
   - Multi-item bundle selection
   - Server-side order locking (/api/orders/prepare)
   - PayPal Orders v2 Sandbox creation (/api/orders/<id>/create-paypal-order)
   - Buyer approval (/api/orders/<id>/simulate-approval)
   - Server-side capture & mathematical verification (/api/orders/<id>/capture)
2. Security & Guardrails:
   - Zero-assumption of payment (creation != captured)
   - Price & currency tampering prevention
   - Pay in 4 affordability transparency and credit eligibility disclosures
3. Emergency Expense (Laptop) Flow
"""

import sys
import json
from app import create_app
from app.config import Config
from app.database import init_db
from app.services.order_service import OrderService
from app.services.paypal_service import PayPalService


def run_demo():
    print("=" * 80)
    print("  PAYPILOT AI 2.0 — PAYPAL SANDBOX INTEGRATION & SECURITY DEMO")
    print("  Owner: Suryansh (PayPal Integration & Security)")
    print("=" * 80)

    class DemoConfig(Config):
        TESTING = True

    app = create_app(DemoConfig)
    with app.app_context():
        # Ensure database is initialized
        init_db()

        # -------------------------------------------------------------
        # SCENARIO 1: College Dorm Moving Bundle ($150 Budget)
        # -------------------------------------------------------------
        print("\n" + "#" * 80)
        print("SCENARIO 1: COLLEGE DORM MOVING BUNDLE ($150 BUDGET)")
        print("Items: TaoTronics Desk Lamp + Conair Steamer + Anker Space A40 Earbuds")
        print("#" * 80)

        item_ids = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"]
        stated_budget = 150.00

        print("\n[STEP 1] Locking Order on Server (Pre-checkout Protection)...")
        prepared = OrderService.prepare_order(item_ids=item_ids, stated_budget=stated_budget)
        order_id = prepared["order_id"]
        total_amount = prepared["total_amount"]

        print(f"  ✓ Order Created: {order_id}")
        print(f"  ✓ Subtotal: ${prepared['subtotal']:.2f}")
        print(f"  ✓ Total Locked: ${total_amount:.2f} {prepared['currency']}")
        print(f"  ✓ Items ({len(prepared['items'])}):")
        for item in prepared["items"]:
            print(f"    - {item['name']} (${item['unit_amount']})")

        # Pay in 4 info
        p4 = prepared["pay_in_4_estimate"]
        print(f"\n[Pay in 4 Disclosure Check]:")
        print(f"  ✓ Eligible for estimate: {p4['eligible_for_estimate']}")
        print(f"  ✓ 4 Bi-weekly installments: ${p4['installment_amount']:.2f} each")
        print(f"  ✓ Affordability Warning: {p4['affordability_warning']}")
        print(f"  ✓ Eligibility Disclaimer: {p4['eligibility_disclaimer']}")

        # Step 2: Create PayPal Sandbox Order
        print("\n[STEP 2] Creating PayPal Orders v2 Sandbox Order...")
        paypal_order = OrderService.create_paypal_order(
            order_id=order_id,
            return_url="http://localhost:3000/checkout/success",
            cancel_url="http://localhost:3000/checkout/cancel"
        )
        paypal_id = paypal_order["paypal_order_id"]
        approval_url = paypal_order["approval_url"]

        print(f"  ✓ PayPal Order ID: {paypal_id}")
        print(f"  ✓ Buyer Approval URL: {approval_url}")
        print(f"  ✓ Status: {paypal_order['status']}")
        print(f"  🛡️ Guardrail Check: {paypal_order['security_notice']}")

        # Verify DB state is still PENDING_APPROVAL
        order_state = OrderService.get_order(order_id)
        assert order_state["status"] == "PENDING_APPROVAL"
        assert order_state["captured_at"] is None
        print("  ✓ Verified: Order is NOT marked paid in server database.")

        # Step 3: Simulate Buyer Approval
        print("\n[STEP 3] Buyer Reviews and Approves on PayPal Sandbox...")
        app_res = OrderService.simulate_buyer_approval(order_id)
        print(f"  ✓ PayPal Approval Recorded: Status = {app_res['status']}")

        order_state = OrderService.get_order(order_id)
        assert order_state["status"] == "APPROVED"
        assert order_state["captured_at"] is None
        print("  🛡️ Guardrail Check: Order is APPROVED by buyer, but STILL NOT marked paid or verified.")

        # Step 4: Server-Side Capture and Verification
        print("\n[STEP 4] Server-Side Capture & Strict Mathematical Verification...")
        verification = OrderService.verify_and_capture_order(order_id=order_id)
        print(f"  ✓ Payment Verified: {verification['verified']}")
        print(f"  ✓ Final Status: {verification['status']}")
        print(f"  ✓ Verified Captured Amount: ${verification['captured_amount']:.2f} {verification['currency']}")
        print(f"  ✓ Captured Timestamp: {verification['captured_at']}")
        print(f"  ✓ Server Message: {verification['message']}")

        # Confirm database update
        final_db = OrderService.get_order(order_id)
        assert final_db["status"] == "CAPTURED"
        print("  ✓ Database record finalized as CAPTURED.")

        # -------------------------------------------------------------
        # SCENARIO 2: Fraud & Tampering Prevention Test
        # -------------------------------------------------------------
        print("\n" + "#" * 80)
        print("SCENARIO 2: SECURITY & TAMPERING PREVENTION GUARDRAILS")
        print("#" * 80)
        fake_order = OrderService.prepare_order(item_ids=["lamp-taotronics-pro"])
        fake_id = fake_order["order_id"]
        print(f"  ✓ Prepared Order {fake_id} for ${fake_order['total_amount']:.2f}")

        print("  [Security Test] Attacker attempts to forge captured payment of $10.00 instead of $32.99...")
        tampered_result = OrderService.verify_and_capture_order(
            order_id=fake_id,
            paypal_order_id="SANDBOX-FORGED-ID",
            captured_amount=10.00,
            captured_currency="USD"
        )
        print(f"  🛡️ Verification Status: {tampered_result['status']}")
        print(f"  🛡️ Rejected: {tampered_result['error']}")
        assert tampered_result["verified"] is False

        # -------------------------------------------------------------
        # SCENARIO 3: Emergency Expense (Laptop) Flow
        # -------------------------------------------------------------
        print("\n" + "#" * 80)
        print("SCENARIO 3: EMERGENCY EXPENSE NAVIGATOR — LAPTOP REPLACEMENT")
        print("#" * 80)
        laptop_order = OrderService.prepare_order(item_ids=["laptop-thinkpad-t14s-refurb"], stated_budget=500.00)
        lid = laptop_order["order_id"]
        print(f"  ✓ Urgent Replacement Locked: {laptop_order['items'][0]['name']}")
        print(f"  ✓ Total: ${laptop_order['total_amount']:.2f} USD")
        lp4 = laptop_order["pay_in_4_estimate"]
        print(f"  ✓ Pay in 4 Available: 4 x ${lp4['installment_amount']:.2f} = ${lp4['total_purchase_amount']:.2f}")

        # Complete full flow
        OrderService.create_paypal_order(lid)
        OrderService.simulate_buyer_approval(lid)
        lap_verified = OrderService.verify_and_capture_order(lid)
        print(f"  ✓ Verified Captured: ${lap_verified['captured_amount']:.2f} {lap_verified['currency']}")
        print(f"  ✓ Order Status: {lap_verified['status']}")

    print("\n" + "=" * 80)
    print("  ALL SURYANSH WORK DELIVERABLES TESTED AND VERIFIED SUCCESSFULLY!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_demo()

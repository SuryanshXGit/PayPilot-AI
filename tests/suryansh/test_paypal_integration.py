import json
import pytest
from app.services.paypal_service import PayPalService
from app.services.order_service import OrderService


def test_paypal_service_configuration(client):
    """Test that PayPal configuration is properly loaded and handles credentials."""
    cfg = PayPalService.get_config()
    assert "client_id" in cfg
    assert "api_base" in cfg
    assert "sandbox.paypal.com" in cfg["api_base"]
    assert cfg["env"] == "sandbox"

    # In default test environment without real secrets, it safely uses simulation mode
    token = PayPalService.get_access_token()
    assert token is not None
    assert len(token) > 0


def test_full_paypal_sandbox_checkout_lifecycle(client):
    """
    Test the full PayPal Sandbox lifecycle:
    Prepare -> Create PayPal Order -> Buyer Approval -> Server-Side Capture & Verify.
    Verifies that order creation or approval opening is NEVER treated as proof of payment.
    """
    # 1. Prepare Order
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00
    })
    assert prep_res.status_code == 201
    order = prep_res.get_json()["order"]
    order_id = order["order_id"]
    assert order["status"] == "CREATED"
    assert order["total_amount"] == 137.97

    # 2. Create PayPal Sandbox Order
    create_res = client.post(f"/api/orders/{order_id}/create-paypal-order", json={
        "return_url": "http://localhost:3000/checkout/success",
        "cancel_url": "http://localhost:3000/checkout/cancel"
    })
    assert create_res.status_code == 200
    paypal_data = create_res.get_json()["paypal_order"]
    paypal_order_id = paypal_data["paypal_order_id"]
    assert paypal_order_id.startswith("SANDBOX-")
    assert "sandbox.paypal.com" in paypal_data["approval_url"]
    assert paypal_data["status"] == "PENDING_APPROVAL"

    # Guardrail Check 1: Order must NOT be marked CAPTURED or PAID
    check_res = client.get(f"/api/orders/{order_id}")
    assert check_res.get_json()["order"]["status"] == "PENDING_APPROVAL"
    assert check_res.get_json()["order"]["captured_at"] is None

    # 3. Simulate Buyer Approval on PayPal Checkout
    approve_res = client.post(f"/api/orders/{order_id}/simulate-approval")
    assert approve_res.status_code == 200
    assert approve_res.get_json()["result"]["status"] == "APPROVED"

    # Guardrail Check 2: Buyer approval alone is STILL NOT captured / proof of payment
    check_res2 = client.get(f"/api/orders/{order_id}")
    assert check_res2.get_json()["order"]["status"] == "APPROVED"
    assert check_res2.get_json()["order"]["captured_at"] is None

    # 4. Server-Side Capture & Verification
    cap_res = client.post(f"/api/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    verification = cap_res.get_json()["verification"]
    assert verification["verified"] is True
    assert verification["status"] == "CAPTURED"
    assert verification["captured_amount"] == 137.97
    assert verification["currency"] == "USD"
    assert verification["captured_at"] is not None

    # Guardrail Check 3: Now and only now is the order verified as CAPTURED in DB
    final_res = client.get(f"/api/orders/{order_id}")
    final_order = final_res.get_json()["order"]
    assert final_order["status"] == "CAPTURED"
    assert final_order["paypal_order_id"] == paypal_order_id
    assert final_order["captured_at"] is not None


def test_tampered_amount_rejection_security(client):
    """
    Security test: Attempting to verify or capture an amount that differs
    from the server-locked catalogue total must be strictly rejected.
    """
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo"],
        "stated_budget": 100.00
    })
    order_id = prep_res.get_json()["order"]["order_id"]
    locked_total = prep_res.get_json()["order"]["total_amount"]  # 77.98

    # Attempt to verify with a manipulated/lower amount
    tampered_amount = 50.00
    tamper_res = client.post("/api/orders/verify-capture", json={
        "order_id": order_id,
        "paypal_order_id": "SANDBOX-FAKE-ID",
        "captured_amount": tampered_amount,
        "captured_currency": "USD"
    })
    assert tamper_res.status_code == 400
    res_data = tamper_res.get_json()
    assert res_data["verification"]["verified"] is False
    assert res_data["verification"]["status"] == "VERIFICATION_FAILED"
    assert "discrepancy" in res_data["verification"]["error"]


def test_currency_mismatch_rejection_security(client):
    """
    Security test: Attempting to capture in a non-matching currency
    must be strictly rejected.
    """
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro"]
    })
    order_id = prep_res.get_json()["order"]["order_id"]

    res = client.post("/api/orders/verify-capture", json={
        "order_id": order_id,
        "paypal_order_id": "SANDBOX-CURR-TEST",
        "captured_amount": 32.99,
        "captured_currency": "EUR"  # Discrepancy: Expected USD
    })
    assert res.status_code == 400
    assert res.get_json()["verification"]["verified"] is False
    assert "discrepancy" in res.get_json()["verification"]["error"]


def test_premature_capture_rejection(client):
    """
    Security test: Calling capture before the buyer has approved the payment
    must fail cleanly with an unapproved payment error.
    """
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro"]
    })
    order_id = prep_res.get_json()["order"]["order_id"]

    # Create PayPal order (buyer has NOT approved yet)
    client.post(f"/api/orders/{order_id}/create-paypal-order")

    # Attempt capture immediately without approval
    cap_res = client.post(f"/api/orders/{order_id}/capture")
    assert cap_res.status_code == 400
    assert cap_res.get_json()["verification"]["verified"] is False
    assert "not approved" in cap_res.get_json()["verification"]["error"].lower()


def test_order_cancellation_flow(client):
    """
    Test handling when a buyer cancels the PayPal checkout process.
    """
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro", "buds-anker-space-a40"]
    })
    order_id = prep_res.get_json()["order"]["order_id"]

    # Create PayPal order
    client.post(f"/api/orders/{order_id}/create-paypal-order")

    # Cancel order
    cancel_res = client.post(f"/api/orders/{order_id}/cancel", json={
        "reason": "Buyer decided to keep looking"
    })
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["order"]["status"] == "CANCELLED"

    # Verify order cannot be captured once cancelled
    cap_res = client.post(f"/api/orders/{order_id}/capture")
    assert cap_res.status_code == 400
    assert "cancelled" in cap_res.get_json()["verification"]["error"].lower()


def test_pay_in_4_calculations_and_disclaimers(client):
    """
    Test Pay in 4 calculator and compliance with hackathon safety checklist:
    - Never treat installment as proof of affordability.
    - Full purchase total must be shown.
    - Explicit disclaimer that Pay in 4 is subject to PayPal eligibility/credit approval.
    """
    # 1. Qualifying order: $137.97
    calc_res = PayPalService.calculate_pay_in_4(137.97, "USD")
    assert calc_res["eligible_for_estimate"] is True
    assert calc_res["total_purchase_amount"] == 137.97
    assert calc_res["installment_count"] == 4
    assert calc_res["installment_amount"] == 34.49
    # Check disclaimers
    assert "does not reduce your total financial obligation" in calc_res["affordability_warning"]
    assert "137.97" in calc_res["affordability_warning"]
    assert "subject to consumer eligibility and credit checks" in calc_res["eligibility_disclaimer"]
    assert len(calc_res["payment_schedule"]) == 4

    # 2. Non-qualifying order (below $30 limit)
    calc_small = PayPalService.calculate_pay_in_4(15.00, "USD")
    assert calc_small["eligible_for_estimate"] is False

    # 3. Via GET endpoint
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"]
    })
    order_id = prep_res.get_json()["order"]["order_id"]
    endpoint_res = client.get(f"/api/orders/{order_id}/pay-in-4")
    assert endpoint_res.status_code == 200
    data = endpoint_res.get_json()["pay_in_4"]
    assert data["eligible_for_estimate"] is True
    assert data["total_purchase_amount"] == 137.97


def test_end_to_end_dorm_bundle_scenario(client):
    """
    End-to-End Test: College Dorm Bundle ($150 Budget)
    AI Multi-Constraint Optimizer -> Budget Guard Verification -> PayPal Sandbox Checkout -> Captured.
    """
    # 1. Shubhneet's Multi-Item Optimizer recommends the optimal dorm bundle
    opt_res = client.post("/api/budget-guard/optimize-bundle", json={
        "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
        "stated_budget": 150.00,
        "priority": "reliability"
    })
    assert opt_res.status_code == 200
    rec_bundle = opt_res.get_json()["result"]["recommended_bundle"]
    assert rec_bundle["is_within_budget"] is True
    assert rec_bundle["total_cost"] == 137.97
    chosen_ids = [item["id"] for item in rec_bundle["items"]]

    # 2. Suryansh's Pre-Order Locking
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": chosen_ids,
        "stated_budget": 150.00
    })
    assert prep_res.status_code == 201
    order_id = prep_res.get_json()["order"]["order_id"]

    # 3. Create PayPal Sandbox Order
    create_res = client.post(f"/api/orders/{order_id}/create-paypal-order")
    assert create_res.status_code == 200
    paypal_order_id = create_res.get_json()["paypal_order"]["paypal_order_id"]

    # 4. Simulate Buyer Approval
    app_res = client.post(f"/api/orders/{order_id}/simulate-approval")
    assert app_res.status_code == 200

    # 5. Server Captures & Verifies
    cap_res = client.post(f"/api/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    assert cap_res.get_json()["verification"]["verified"] is True
    assert cap_res.get_json()["verification"]["captured_amount"] == 137.97

    # 6. Final verification in database
    final_order = client.get(f"/api/orders/{order_id}").get_json()["order"]
    assert final_order["status"] == "CAPTURED"
    assert final_order["total_amount"] == 137.97
    assert len(final_order["items"]) == 3


def test_end_to_end_emergency_laptop_scenario(client):
    """
    End-to-End Test: Emergency Replacement Laptop Scenario
    Verifies emergency item locking, Pay in 4 schedule, and verified capture.
    """
    # 1. Lock emergency refurbished laptop
    prep_res = client.post("/api/orders/prepare", json={
        "item_ids": ["laptop-thinkpad-t14s-refurb"],
        "stated_budget": 500.00
    })
    assert prep_res.status_code == 201
    order_data = prep_res.get_json()["order"]
    order_id = order_data["order_id"]
    assert order_data["total_amount"] == 499.00

    # 2. Verify Pay in 4 breakdown for emergency expense
    p4 = order_data["pay_in_4_estimate"]
    assert p4["eligible_for_estimate"] is True
    assert p4["total_purchase_amount"] == 499.00
    assert p4["installment_amount"] == 124.75

    # 3. Execute PayPal Sandbox Checkout
    client.post(f"/api/orders/{order_id}/create-paypal-order")
    client.post(f"/api/orders/{order_id}/simulate-approval")
    cap_res = client.post(f"/api/orders/{order_id}/capture")
    assert cap_res.status_code == 200
    assert cap_res.get_json()["verification"]["verified"] is True
    assert cap_res.get_json()["verification"]["captured_amount"] == 499.00

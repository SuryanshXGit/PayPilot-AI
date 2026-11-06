import json


def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True
    assert data["database"]["catalogue_products_count"] > 0


def test_api_products_list(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert "data_source_disclosure" in data


def test_api_products_filter(client):
    response = client.get("/api/products?category=desk_lamp&max_price=40.00")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    for p in data["products"]:
        assert p["category"] == "desk_lamp"
        assert p["price"] <= 40.00


def test_api_product_detail(client):
    response = client.get("/api/products/lamp-taotronics-pro")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["product"]["id"] == "lamp-taotronics-pro"
    assert data["product"]["price"] == 32.99


def test_api_price_history_disclosure(client):
    response = client.get("/api/products/lamp-taotronics-pro/price-history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["price_history"]["history_data_source"] == "simulated_honey_trend"


def test_api_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    cats = {c["category"] for c in data["categories"]}
    assert "desk_lamp" in cats
    assert "laptop" in cats


def test_api_budget_guard_check_under_budget(client):
    payload = {
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00,
        "include_bills": True
    }
    response = client.post(
        "/api/budget-guard/check",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    res = data["result"]
    assert res["status"] == "UNDER_BUDGET"
    assert res["is_over_budget"] is False
    assert res["pricing_breakdown"]["total"] == 137.97
    assert res["difference"] == 12.03


def test_api_budget_guard_optimize_bundle(client):
    payload = {
        "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
        "stated_budget": 150.00,
        "priority": "reliability"
    }
    response = client.post(
        "/api/budget-guard/optimize-bundle",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    res = data["result"]
    assert res["recommended_bundle"]["is_within_budget"] is True
    assert res["recommended_bundle"]["total_cost"] == 137.97
    assert len(res["trade_off_explanations"]) > 0


def test_api_budget_guard_alternatives(client):
    payload = {
        "current_item_ids": ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00
    }
    response = client.post(
        "/api/budget-guard/alternatives",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response.status_code == 200
    data = response.get_json()
    res = data["result"]
    assert res["is_over_budget"] is True
    assert len(res["viable_swaps"]) > 0


def test_api_bills_crud_and_summary(client):
    # List bills
    res_list = client.get("/api/bills")
    assert res_list.status_code == 200
    assert res_list.get_json()["count"] >= 4

    # Summary
    res_summary = client.get("/api/bills/summary?shopping_budget=150.00&reference_date=2026-11-02")
    assert res_summary.status_code == 200
    summary_data = res_summary.get_json()["summary"]
    assert summary_data["upcoming_bills_total"] == 80.00
    assert summary_data["shopping_budget_analysis"]["disposable_shopping_budget_after_bills"] == 70.00


def test_api_order_prepare_and_verify_capture(client):
    # 1. Prepare Order
    prepare_payload = {
        "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
        "stated_budget": 150.00
    }
    prep_res = client.post(
        "/api/orders/prepare",
        data=json.dumps(prepare_payload),
        content_type="application/json"
    )
    assert prep_res.status_code == 201
    order_data = prep_res.get_json()["order"]
    order_id = order_data["order_id"]
    assert order_data["total_amount"] == 137.97
    assert order_data["ready_for_paypal_checkout"] is True
    assert "purchase_units" in order_data["paypal_create_order_payload"]

    # 2. Try verifying with tampered/incorrect amount
    tamper_payload = {
        "order_id": order_id,
        "paypal_order_id": "PAYPAL-TEST-1234",
        "captured_amount": 100.00,  # Mismatch! Expected 137.97
        "captured_currency": "USD"
    }
    tamper_res = client.post(
        "/api/orders/verify-capture",
        data=json.dumps(tamper_payload),
        content_type="application/json"
    )
    assert tamper_res.status_code == 400
    assert tamper_res.get_json()["verification"]["verified"] is False

    # 3. Verify with exact captured amount
    success_payload = {
        "order_id": order_id,
        "paypal_order_id": "PAYPAL-TEST-5678",
        "captured_amount": 137.97,  # Exact match!
        "captured_currency": "USD"
    }
    success_res = client.post(
        "/api/orders/verify-capture",
        data=json.dumps(success_payload),
        content_type="application/json"
    )
    assert success_res.status_code == 200
    assert success_res.get_json()["verification"]["verified"] is True
    assert success_res.get_json()["verification"]["status"] == "CAPTURED"

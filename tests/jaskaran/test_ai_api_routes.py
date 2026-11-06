"""
Integration tests for AI REST API endpoints (/api/ai/*)
Module Owner: Jaskaran
"""

import json
import pytest


def test_api_parse_intent(client):
    res = client.post("/api/ai/parse-intent", json={
        "prompt": "I need a desk lamp and steamer under $100. Prioritize lowest cost."
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["result"]["stated_budget"] == 100.0
    assert "desk_lamp" in data["result"]["categories"]
    assert "portable_steamer" in data["result"]["categories"]


def test_api_recommend_bundle_dorm(client):
    res = client.post("/api/ai/recommend-bundle", json={
        "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
        "stated_budget": 150.0,
        "priority": "reliability"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["recommended_bundle"]["total_cost"] == 137.97
    assert data["recommended_bundle"]["is_within_budget"] is True
    assert len(data["trade_off_explanations"]) >= 3


def test_api_chat(client):
    res = client.post("/api/ai/chat", json={
        "session_id": "route_test_session",
        "message": "I'm moving into an unfurnished dorm with strict $150 budget. Need lamp, steamer, and buds."
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "reply_text" in data
    assert data["bundle"] is not None
    assert data["bundle"]["total_cost"] == 137.97


def test_api_voice_command_payment_guardrail(client):
    res = client.post("/api/ai/voice-command", json={
        "transcript": "Checkout with PayPal Sandbox",
        "current_bundle_total": 137.97
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["result"]["requires_explicit_confirmation"] is True
    assert data["result"]["is_payment_action"] is True


def test_api_smart_filter(client):
    res = client.post("/api/ai/smart-filter", json={
        "sender": "alerts@paypa1-security.xyz",
        "subject": "Account suspended",
        "body": "Click here to verify password immediately."
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["result"]["category"] == "SUSPICIOUS"


def test_api_scenarios(client):
    res = client.get("/api/ai/scenarios")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["scenarios"]) >= 2

"""
Unit tests for AIIntentParser
Module Owner: Jaskaran
"""

import pytest
from app.services.ai_intent_parser import AIIntentParser


def test_parse_college_dorm_prompt():
    prompt = (
        "I'm a college student moving into an unfurnished dorm with a strict $150 total budget. "
        "I need a desk lamp, a portable steamer, and noise-cancelling study buds. "
        "Prioritize reliability and explain compromises."
    )
    result = AIIntentParser.parse(prompt)

    assert result["stated_budget"] == 150.0
    assert result["budget_type"] == "strict"
    assert "desk_lamp" in result["categories"]
    assert "portable_steamer" in result["categories"]
    assert "noise_cancelling_earbuds" in result["categories"]
    assert len(result["categories"]) == 3
    assert result["priority"] == "reliability"
    assert result["context"] == "college_dorm"
    assert result["intent_type"] == "MULTI_ITEM_OPTIMIZATION"
    assert result["confidence_score"] >= 0.8


def test_parse_emergency_laptop_prompt():
    prompt = "My work laptop broke and I need an urgent replacement under $500 with fast 1-day delivery."
    result = AIIntentParser.parse(prompt)

    assert result["stated_budget"] == 500.0
    assert "laptop" in result["categories"]
    assert result["context"] == "emergency_expense"
    assert result["intent_type"] == "EMERGENCY_OPTIMIZATION"


def test_parse_tradeoff_query():
    prompt = "Why did you pick TaoTronics desk lamp instead of BenQ?"
    result = AIIntentParser.parse(prompt)

    assert result["intent_type"] == "TRADE_OFF_QUERY"
    assert "desk_lamp" in result["categories"]


def test_parse_budget_adjustment():
    prompt = "What if my new budget is $120?"
    result = AIIntentParser.parse(prompt)

    assert result["intent_type"] == "BUDGET_ADJUSTMENT"
    assert result["stated_budget"] == 120.0


def test_parse_swap_request():
    prompt = "Swap the lamp for the cheapest one"
    result = AIIntentParser.parse(prompt)

    assert result["intent_type"] == "SWAP_REQUEST"


def test_parse_checkout_intent():
    prompt = "Proceed to checkout with PayPal now"
    result = AIIntentParser.parse(prompt)

    assert result["intent_type"] == "CHECKOUT_INTENT"

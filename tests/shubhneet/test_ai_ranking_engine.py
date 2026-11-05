"""
Unit tests for AIRankingEngine
Module Owner: Shubhneet
"""

import pytest
from app.services.ai_ranking_engine import AIRankingEngine
from app.services.catalogue_service import CatalogueService


def test_score_individual_product(app_context):
    prods = CatalogueService.get_all_products(category="desk_lamp")
    assert len(prods) > 0
    p = prods[0]
    weights = {"reliability": 0.55, "cost": 0.25, "delivery_speed": 0.10, "warranty": 0.10}
    score = AIRankingEngine.score_product(p, weights, max_price_ref=100.0)

    assert 0.0 <= score <= 100.0


def test_optimize_dorm_basket_150_budget(app_context):
    categories = ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"]
    result = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=150.0,
        priority="reliability"
    )

    assert result["status"] == "success"
    assert result["total_combinations_evaluated"] == 36
    assert result["feasible_combinations_count"] > 0

    rec = result["recommended_bundle"]
    assert rec is not None
    assert rec["total_cost"] <= 150.0
    assert rec["is_within_budget"] is True
    # The expected optimal combination: TaoTronics (32.99) + Conair (44.99) + Anker Space A40 (59.99) = 137.97
    assert rec["total_cost"] == 137.97
    assert rec["surplus"] == 12.03
    assert rec["average_reliability"] > 9.0

    # Budget saver check
    saver = result["budget_saver_bundle"]
    assert saver is not None
    assert saver["total_cost"] <= rec["total_cost"]
    assert saver["total_cost"] == 68.97

    # Premium benchmark check
    prem = result["premium_bundle"]
    assert prem is not None
    assert prem["total_cost"] > 150.0  # BenQ + Conair + Sony exceeds $150


def test_optimize_emergency_laptop_speed_priority(app_context):
    categories = ["laptop"]
    result = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=500.0,
        priority="delivery_speed"
    )

    assert result["status"] == "success"
    rec = result["recommended_bundle"]
    assert rec is not None
    # Lenovo ThinkPad T14s Refurbished ($499.00) has 1-day delivery and 9.6 rating
    assert rec["items"][0].id == "laptop-thinkpad-t14s-refurb"
    assert rec["max_delivery_days"] == 1

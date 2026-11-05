"""
Unit tests for AITradeOffExplainer
Module Owner: Shubhneet
"""

import pytest
from app.services.ai_ranking_engine import AIRankingEngine
from app.services.ai_tradeoff_explainer import AITradeOffExplainer
from app.services.catalogue_service import CatalogueService


def test_explain_dorm_recommendation(app_context):
    categories = ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"]
    opt_res = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=150.0,
        priority="reliability"
    )

    explanations = AITradeOffExplainer.explain_bundle_recommendation(
        recommended_bundle=opt_res["recommended_bundle"],
        budget_saver_bundle=opt_res["budget_saver_bundle"],
        premium_bundle=opt_res["premium_bundle"],
        stated_budget=150.0,
        priority="reliability",
        category_products=opt_res["category_products"]
    )

    assert len(explanations) >= 3
    full_text = " ".join(explanations)

    # Check key trade-off elements called out in Hackathon PDF:
    assert "$137.97" in full_text
    assert "surplus" in full_text.lower()
    assert "taotronics" in full_text.lower()
    assert "benq" in full_text.lower()


def test_explain_over_budget_scenario(app_context):
    # If budget is $50, no combination of 3 items can fit!
    categories = ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"]
    opt_res = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=50.0,
        priority="reliability"
    )

    explanations = AITradeOffExplainer.explain_bundle_recommendation(
        recommended_bundle=opt_res["recommended_bundle"],
        budget_saver_bundle=opt_res["budget_saver_bundle"],
        premium_bundle=opt_res["premium_bundle"],
        stated_budget=50.0,
        priority="reliability",
        category_products=opt_res["category_products"]
    )

    full_text = " ".join(explanations)
    assert "shortfall" in full_text.lower()
    assert "constraint" in full_text.lower()


def test_explain_emergency_laptop_tradeoff(app_context):
    thinkpad = CatalogueService.get_product_by_id("laptop-thinkpad-t14s-refurb")
    acer = CatalogueService.get_product_by_id("laptop-acer-aspire5")

    explanations = AITradeOffExplainer.explain_emergency_scenario(
        selected_product=thinkpad,
        alternative_product=acer,
        stated_budget=500.0,
        emergency_context="broken_laptop"
    )

    assert len(explanations) >= 2
    full_text = " ".join(explanations)
    assert "turnaround" in full_text.lower() or "1-day" in full_text.lower()
    assert "warranty" in full_text.lower()

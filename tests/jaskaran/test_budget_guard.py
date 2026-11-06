from app.services.budget_guard import BudgetGuardService


def test_budget_guard_under_budget(app):
    with app.app_context():
        # TaoTronics ($32.99) + Conair ($44.99) + Anker ($59.99) = $137.97
        item_ids = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"]
        result = BudgetGuardService.check_bundle(
            item_ids=item_ids,
            stated_budget=150.00
        )
        assert result["status"] == "UNDER_BUDGET"
        assert result["is_over_budget"] is False
        assert result["pricing_breakdown"]["total"] == 137.97
        assert result["difference"] == 12.03
        assert result["amount_remaining"] == 12.03
        assert result["average_reliability_score"] == 9.33


def test_budget_guard_over_budget_detection(app):
    with app.app_context():
        # BenQ ($89.00) + Conair ($44.99) + Anker ($59.99) = $193.98
        item_ids = ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"]
        result = BudgetGuardService.check_bundle(
            item_ids=item_ids,
            stated_budget=150.00
        )
        assert result["status"] == "OVER_BUDGET"
        assert result["is_over_budget"] is True
        assert result["pricing_breakdown"]["total"] == 193.98
        assert result["amount_over"] == 43.98
        assert "exceeds" in result["status_message"]


def test_budget_guard_multi_item_optimizer_dorm_scenario(app):
    """
    Test the jaw-dropping demo scenario:
    College student moving into dorm with strict $150 budget needing:
    - desk lamp
    - portable steamer
    - noise-cancelling earbuds
    Prioritizing reliability.
    """
    with app.app_context():
        categories = ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"]
        budget = 150.00
        result = BudgetGuardService.optimize_bundle(
            categories=categories,
            stated_budget=budget,
            priority="reliability"
        )

        assert result["stated_budget"] == 150.00
        assert result["feasible_combinations_count"] > 0

        # Recommended bundle must be <= $150
        rec = result["recommended_bundle"]
        assert rec is not None
        assert rec["is_within_budget"] is True
        assert rec["total_cost"] <= 150.00

        # Optimal reliability selection is TaoTronics + Conair + Anker Space A40
        rec_ids = {p["id"] for p in rec["items"]}
        assert "lamp-taotronics-pro" in rec_ids
        assert "steamer-conair-turbo" in rec_ids
        assert "buds-anker-space-a40" in rec_ids
        assert rec["total_cost"] == 137.97
        assert rec["average_reliability"] == 9.33

        # Budget saver option must be cheaper
        saver = result["budget_saver_bundle"]
        assert saver["total_cost"] < rec["total_cost"]
        assert saver["total_cost"] == 68.97

        # Explanations generated
        assert len(result["trade_off_explanations"]) >= 1


def test_budget_guard_suggest_alternatives_for_over_budget(app):
    """
    When user selects BenQ lamp ($89) + Conair ($44.99) + Anker ($59.99) = $193.98,
    Budget Guard must suggest swapping BenQ lamp to TaoTronics or Lumina to get under $150.
    """
    with app.app_context():
        over_budget_ids = ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"]
        result = BudgetGuardService.suggest_alternatives_for_over_budget(
            current_item_ids=over_budget_ids,
            stated_budget=150.00
        )

        assert result["is_over_budget"] is True
        assert result["shortfall"] == 43.98
        assert len(result["viable_swaps"]) > 0

        # Verify that each suggested swap results in a total <= 150.00
        for swap in result["viable_swaps"]:
            assert swap["new_bundle_total"] <= 150.00
            assert swap["savings"] >= 43.98


def test_budget_guard_with_upcoming_bills_awareness(app):
    """
    Proactive Financial Health test:
    Total bills due within 7 days = $45 (electric) + $35 (WiFi) = $80.00.
    Stated budget = $150.00.
    Remaining disposable budget = $70.00.
    An item bundle of $137.97 is under $150, but over the disposable budget ($70.00)!
    """
    with app.app_context():
        item_ids = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"]  # $137.97
        result = BudgetGuardService.check_bundle(
            item_ids=item_ids,
            stated_budget=150.00,
            include_bills=True,
            bills_due_within_days=7
        )

        assert "bill_awareness" in result
        bill_info = result["bill_awareness"]
        assert bill_info["upcoming_bills_total"] == 80.00
        assert bill_info["disposable_budget_after_bills"] == 70.00
        assert bill_info["is_over_disposable_budget"] is True
        assert "Warning" in bill_info["advisory"]

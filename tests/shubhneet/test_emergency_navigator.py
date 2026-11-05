from app.services.catalogue_service import CatalogueService
from app.services.budget_guard import BudgetGuardService


def test_emergency_laptop_options(app):
    with app.app_context():
        laptops = CatalogueService.get_all_products(category="laptop")
        assert len(laptops) >= 2

        # Check emergency priority delivery item
        urgent_refurb = next((l for l in laptops if l.id == "laptop-thinkpad-t14s-refurb"), None)
        assert urgent_refurb is not None
        assert urgent_refurb.delivery_days == 1
        assert urgent_refurb.warranty_months == 12
        assert urgent_refurb.reliability_score >= 9.5
        assert urgent_refurb.price == 499.00

        # Check budget alternative
        budget_new = next((l for l in laptops if l.id == "laptop-acer-aspire5"), None)
        assert budget_new is not None
        assert budget_new.price < urgent_refurb.price
        assert budget_new.delivery_days == 2


def test_emergency_expense_budget_guard(app):
    with app.app_context():
        # Scenario: User has emergency fund budget of $450
        # If user picks ThinkPad ($499), Budget Guard flags OVER_BUDGET
        res = BudgetGuardService.check_bundle(
            item_ids=["laptop-thinkpad-t14s-refurb"],
            stated_budget=450.00
        )
        assert res["status"] == "OVER_BUDGET"
        assert res["amount_over"] == 49.00

        # Budget Guard alternatives suggest Acer Aspire ($389.00), saving $110 and fitting under $450
        alternatives = BudgetGuardService.suggest_alternatives_for_over_budget(
            current_item_ids=["laptop-thinkpad-t14s-refurb"],
            stated_budget=450.00
        )
        assert alternatives["is_over_budget"] is True
        assert len(alternatives["viable_swaps"]) >= 1
        swap = alternatives["viable_swaps"][0]
        assert swap["add_item"]["id"] == "laptop-acer-aspire5"
        assert swap["new_bundle_total"] == 389.00
        assert swap["new_surplus"] == 61.00

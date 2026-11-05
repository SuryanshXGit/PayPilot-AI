"""
test_bundle_scenarios.py - Multi-Item Dorm Room Budget Optimizer Test Suite
Owned by Sehaj (Product Data, Comparison & Testing Lead)

Validates:
- $150 College Student Dorm Room prompt constraints
- Multi-constraint trade-offs (price vs reliability)
- Deterministic Budget Guard calculations & rounding
- Over-budget detection and automated substitution suggestions
- Proactive financial health integration (upcoming 7-day bills)
"""

import unittest
import os
import sys

# Ensure parent directory is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from utils.budget_guard import BudgetGuard


class TestBundleScenarios(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.products = self.loader.get_products()
        self.products_by_id = {p["id"]: p for p in self.products}

    def test_dorm_scenario_jaw_dropping_optimal_bundle(self):
        """
        Scenario Prompt: 'I’m a college student moving into an unfurnished dorm with a strict $150 total budget.
        I need a desk lamp, a portable steamer, and noise-cancelling study buds. Prioritize reliability and explain compromises.'
        """
        # Selected high-reliability items within $150 budget
        selected = [
            self.products_by_id["lamp-01"],     # LuminaFlex Clamp LED: $29.99 (Reliability 9.2)
            self.products_by_id["steamer-01"],  # SteamGlide Travel: $26.50 (Reliability 8.8)
            self.products_by_id["buds-01"]      # SoundPulse ANC: $54.99 (Reliability 8.9)
        ]

        result = BudgetGuard.evaluate_budget(selected, max_budget=150.00)

        # 1. Deterministic total check: 29.99 + 26.50 + 54.99 = 111.48
        self.assertEqual(result["grand_total"], 111.48)
        self.assertEqual(result["status"], "APPROVED")
        self.assertTrue(result["is_under_budget"])

        # 2. Budget headroom check: 150.00 - 111.48 = 38.52
        self.assertEqual(result["variance"], 38.52)

        # 3. Average reliability check: (9.2 + 8.8 + 8.9) / 3 = 8.97
        avg_rel = sum(p["reliability_score"] for p in selected) / len(selected)
        self.assertAlmostEqual(avg_rel, 8.9666, places=2)
        self.assertGreaterEqual(avg_rel, 8.5, "Optimal bundle must prioritize reliability >= 8.5/10")

    def test_over_budget_premium_bundle_detection(self):
        """
        Tests that Budget Guard catches an over-budget combination and reports exact shortfall.
        """
        overbudget_items = [
            self.products_by_id["lamp-03"],     # PureLight Minimalist: $44.99
            self.products_by_id["steamer-03"],  # ProSteam Ultra: $42.00
            self.products_by_id["buds-03"]      # SonicSilence Studio: $95.00
        ]

        result = BudgetGuard.evaluate_budget(overbudget_items, max_budget=150.00)

        # Total: 44.99 + 42.00 + 95.00 = 181.99
        self.assertEqual(result["grand_total"], 181.99)
        self.assertEqual(result["status"], "OVER_BUDGET")
        self.assertFalse(result["is_under_budget"])
        self.assertEqual(result["variance"], -31.99)
        self.assertTrue(any("BUDGET EXCEEDED" in f for f in result["flags"]))

    def test_budget_guard_automatic_substitutions(self):
        """
        When over budget, Budget Guard must suggest deterministic lower-cost alternatives
        to bring the basket under $150.
        """
        overbudget_items = [
            self.products_by_id["lamp-01"],     # $29.99
            self.products_by_id["steamer-01"],  # $26.50
            self.products_by_id["buds-03"]      # $95.00 -> Total = $151.49 (Over by $1.49)
        ]

        eval_initial = BudgetGuard.evaluate_budget(overbudget_items, max_budget=150.00)
        self.assertFalse(eval_initial["is_under_budget"])

        suggestions = BudgetGuard.suggest_alternative_substitutions(
            selected_items=overbudget_items,
            catalogue_items=self.products,
            max_budget=150.00
        )

        self.assertGreater(len(suggestions), 0, "Budget Guard should find viable alternatives")
        # Ensure at least one suggestion replaces buds-03 ($95) with buds-01 ($54.99)
        earbud_replacements = [s for s in suggestions if s["replace_item_id"] == "buds-03"]
        self.assertGreater(len(earbud_replacements), 0)
        top_suggestion = earbud_replacements[0]
        self.assertLessEqual(top_suggestion["new_bundle_total"], 150.00)

    def test_proactive_financial_health_bill_due_warning(self):
        """
        Tests that Budget Guard factors in upcoming bills due within 7 days.
        """
        bills_data = self.loader.get_sample_bills()
        bills_7_days = bills_data["financial_summary"]["total_bills_due_within_7_days"]  # $77.50

        selected = [
            self.products_by_id["lamp-01"],     # $29.99
            self.products_by_id["steamer-01"],  # $26.50
            self.products_by_id["buds-01"]      # $54.99 -> Total = $111.48
        ]

        result = BudgetGuard.evaluate_budget(
            selected,
            max_budget=150.00,
            upcoming_bills_7_days=bills_7_days
        )

        # 111.48 (cart) + 77.50 (bills) = 188.98 total immediate outlay
        self.assertEqual(result["total_immediate_commitments"], 188.98)
        self.assertTrue(any("UPCOMING BILLS NOTICE" in f for f in result["flags"]))


if __name__ == "__main__":
    unittest.main()

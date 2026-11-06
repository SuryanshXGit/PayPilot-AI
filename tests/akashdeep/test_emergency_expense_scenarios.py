"""
test_emergency_expense_scenarios.py - Emergency Expense & Urgent Replacement Test Suite
Owned by Akashdeep (Product Data, Comparison & Testing Lead)

Validates:
- Emergency laptop breakdown scenario
- Delivery timing & shipping cost trade-offs
- Warranty & refurbished condition comparison
- Strict compliance: no medical advice, no guaranteed financial relief, no unauthorized assumptions
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from utils.budget_guard import BudgetGuard


class TestEmergencyExpenseScenarios(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.products = self.loader.get_products(category="emergency_laptop")
        self.products_by_id = {p["id"]: p for p in self.products}

    def test_emergency_laptop_urgent_replacement_selection(self):
        """
        User scenario: Broken work laptop with 48-hour project deadline.
        Budget limit: $350.00.
        Requirement: Must arrive next-day and run desktop office software.
        """
        thinkpad = self.products_by_id["laptop-01"]
        self.assertEqual(thinkpad["name"], "Lenovo ThinkPad T490 14\" FHD (Certified Refurbished)")

        # Check next day shipping option exists
        shipping_opts = thinkpad.get("shipping_options", [])
        next_day_opt = next((s for s in shipping_opts if "Next-Day" in s["tier"]), None)
        self.assertIsNotNone(next_day_opt, "Emergency laptop must offer next-day urgent delivery")

        # Calculate basket with urgent shipping ($289.00 item + $15.00 shipping = $304.00)
        cart = [thinkpad]
        result = BudgetGuard.evaluate_budget(cart, max_budget=350.00, shipping_cost=next_day_opt["cost"])

        self.assertEqual(result["grand_total"], 304.00)
        self.assertEqual(result["status"], "APPROVED")
        self.assertEqual(result["variance"], 46.00)

    def test_emergency_expense_warranty_and_condition_data_integrity(self):
        """
        Ensure all emergency items disclose warranty information and refurbished/condition notes.
        """
        for laptop in self.products:
            p_id = laptop["id"]
            warranty = laptop.get("warranty_info")
            self.assertIsNotNone(warranty, f"Laptop {p_id} must have warranty info")
            self.assertIn("simulated", warranty.lower(), f"Laptop {p_id} warranty must be labelled as simulated")

            # Check trade-offs include both pros and compromises
            trade_offs = laptop.get("trade_offs", {})
            self.assertIn("pros", trade_offs)
            self.assertIn("compromises", trade_offs)
            self.assertGreater(len(trade_offs["compromises"]), 0, f"Laptop {p_id} must explain compromises")

    def test_compliance_no_medical_or_unauthorized_relief_claims(self):
        """
        Guardrail check: System must present choices and trade-offs,
        NOT medical advice or guaranteed financial relief.
        """
        scenarios = self.loader.get_demo_scenarios()
        emergency_scenario = next((s for s in scenarios if "emergency" in s["id"]), None)
        self.assertIsNotNone(emergency_scenario)

        forbidden_phrases = [
            "guaranteed loan",
            "free government grant",
            "medical diagnosis",
            "guaranteed debt forgiveness",
            "no credit check required"
        ]

        scenario_str = str(emergency_scenario).lower()
        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, scenario_str, f"Found forbidden misleading phrase: '{phrase}'")


if __name__ == "__main__":
    unittest.main()

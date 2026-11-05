"""
test_data_integrity.py - Catalogue Data Provenance & Guardrails Test Suite
Owned by Sehaj (Product Data, Comparison & Testing Lead)

Validates:
- Strict data provenance labelling (live, sourced, manually entered, or simulated)
- Honey price trend disclaimers
- Proactive bill monitoring boundary checks (no unauthorized bank access)
- Sanity of numeric values (prices, ratings, reliability metrics)
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader


class TestDataIntegrity(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()

    def test_catalogue_provenance_validation(self):
        """All products must include required data_source tags and disclaimers."""
        validation = self.loader.validate_data_provenance()
        self.assertTrue(validation["valid"], f"Provenance validation failed: {validation['errors']}")
        self.assertGreater(validation["total_products_checked"], 0)
        self.assertGreater(validation["total_trends_checked"], 0)

    def test_products_numeric_sanity(self):
        """Ensure prices, ratings, and reliability scores are realistic positive numbers."""
        products = self.loader.get_products()
        for p in products:
            p_id = p["id"]
            self.assertGreater(p["price"], 0, f"Product {p_id} price must be > 0")
            self.assertGreaterEqual(p["rating"], 1.0, f"Product {p_id} rating must be >= 1.0")
            self.assertLessEqual(p["rating"], 5.0, f"Product {p_id} rating must be <= 5.0")
            self.assertGreaterEqual(p["reliability_score"], 1.0, f"Product {p_id} reliability must be >= 1.0")
            self.assertLessEqual(p["reliability_score"], 10.0, f"Product {p_id} reliability must be <= 10.0")

    def test_price_history_integrity_and_disclaimers(self):
        """Price trends must not imply live Honey API connection."""
        trends = self.loader.get_price_trends()
        self.assertGreater(len(trends), 0)

        for p_id, item in trends.items():
            self.assertIn("stats_90_days", item)
            self.assertIn("history_points", item)
            self.assertIn("disclaimer", item)
            self.assertIn("data_source", item)
            self.assertIn("simulated", item["data_source"].lower())
            self.assertIn("simulated", item["disclaimer"].lower())

    def test_sample_bills_provenance(self):
        """Bill records must be labelled as manually entered sample data without bank access."""
        bills_data = self.loader.get_sample_bills()
        meta = bills_data.get("_meta", {})
        self.assertEqual(meta.get("data_source"), "manually_entered_sample")
        self.assertIn("no direct bank account integration", meta.get("disclaimer", "").lower())


if __name__ == "__main__":
    unittest.main()

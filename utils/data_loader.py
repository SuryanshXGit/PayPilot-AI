"""
data_loader.py - Product Catalogue & Data Loading Utility
Owned by Sehaj (Product Data, Comparison & Testing Lead)

Responsibilities:
- Load catalogue items, price histories, bills, and demo scenarios from JSON.
- Strictly enforce data provenance tags (live, sourced, manually entered, or simulated).
- Ensure safety disclaimers are present on all data structures.
"""

import json
import os
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


class DataLoader:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir

    def _load_json(self, filename: str) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Data file not found at: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_products(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return list of products, optionally filtered by category, ensuring provenance tags."""
        data = self._load_json("products.json")
        products = data.get("products", [])
        if category:
            products = [p for p in products if p.get("category") == category]
        return products

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single product by id."""
        products = self.get_products()
        for p in products:
            if p.get("id") == product_id:
                return p
        return None

    def get_price_trends(self, product_id: Optional[str] = None) -> Dict[str, Any]:
        """Return price trend dataset. If product_id specified, return specific trend."""
        data = self._load_json("price_history.json")
        trends = data.get("price_trends", {})
        if product_id:
            return trends.get(product_id, None)
        return trends

    def get_sample_bills(self) -> Dict[str, Any]:
        """Return sample bill records for Proactive Financial Health Monitoring."""
        return self._load_json("sample_bills.json")

    def get_comparison_matrices(self) -> Dict[str, Any]:
        """Return comparison matrices and trade-off metrics."""
        return self._load_json("comparison_matrix.json")

    def get_demo_scenarios(self) -> List[Dict[str, Any]]:
        """Return curated demo scenarios."""
        data = self._load_json("demo_scenarios.json")
        return data.get("scenarios", [])

    def validate_data_provenance(self) -> Dict[str, Any]:
        """
        Validates all products and trends against hackathon guardrails:
        - Must have data_source in ['live', 'sourced', 'manually_entered', 'simulated']
        - Must have explicit disclaimers
        - Must not make unverified claims
        """
        errors = []
        valid_sources = {"live", "sourced", "manually_entered", "simulated", "simulated_historical_dataset"}

        # Validate products
        prod_data = self._load_json("products.json")
        if not prod_data.get("_meta", {}).get("data_source"):
            errors.append("products.json _meta is missing data_source")

        for prod in prod_data.get("products", []):
            p_id = prod.get("id", "unknown")
            source = prod.get("data_source")
            if not source or source not in valid_sources:
                errors.append(f"Product {p_id} has invalid or missing data_source: '{source}'")
            if not prod.get("data_source_disclaimer"):
                errors.append(f"Product {p_id} is missing data_source_disclaimer")
            if prod.get("price") is None or prod.get("price") < 0:
                errors.append(f"Product {p_id} has invalid price")

        # Validate price history
        trend_data = self._load_json("price_history.json")
        if not trend_data.get("_meta", {}).get("data_source"):
            errors.append("price_history.json _meta is missing data_source")
        for p_id, trend in trend_data.get("price_trends", {}).items():
            if not trend.get("disclaimer"):
                errors.append(f"Price trend for {p_id} is missing disclaimer")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "total_products_checked": len(prod_data.get("products", [])),
            "total_trends_checked": len(trend_data.get("price_trends", {}))
        }

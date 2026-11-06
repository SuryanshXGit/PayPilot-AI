"""
comparison_helper.py - Product Comparison & Trade-off Engine
Owned by Akashdeep (Product Data, Comparison & Testing Lead) / Suryansh (Frontend/UI)

Responsibilities:
- Compare items side-by-side across key dimensions (price, reliability, rating, specs).
- Calculate compromise balance scores.
- Generate human-readable trade-off summaries for UI cards and AI responses.
"""

from typing import List, Dict, Any, Optional


class ComparisonHelper:
    @staticmethod
    def compare_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Produce a normalized comparison matrix across provided items.
        """
        if not items:
            return {"items": [], "comparison_points": []}

        comparison = {
            "item_count": len(items),
            "items": [],
            "metrics": {
                "lowest_price": min(item.get("price", 0) for item in items),
                "highest_price": max(item.get("price", 0) for item in items),
                "highest_reliability": max(item.get("reliability_score", 0) for item in items),
                "highest_rating": max(item.get("rating", 0) for item in items)
            }
        }

        for item in items:
            item_entry = {
                "id": item.get("id"),
                "name": item.get("name"),
                "category": item.get("category"),
                "price": item.get("price"),
                "rating": item.get("rating"),
                "reliability_score": item.get("reliability_score"),
                "trade_offs": item.get("trade_offs", {}),
                "warranty_info": item.get("warranty_info"),
                "shipping_options": item.get("shipping_options", []),
                "data_source": item.get("data_source", "simulated")
            }
            comparison["items"].append(item_entry)

        return comparison

    @staticmethod
    def generate_trade_off_explanation(item_a: Dict[str, Any], item_b: Dict[str, Any]) -> str:
        """
        Generate natural language trade-off comparison between two items in the same category.
        """
        price_diff = item_b.get("price", 0) - item_a.get("price", 0)
        rel_diff = item_b.get("reliability_score", 0) - item_a.get("reliability_score", 0)

        if price_diff > 0:
            more_expensive = item_b
            cheaper = item_a
            diff_amt = price_diff
        else:
            more_expensive = item_a
            cheaper = item_b
            diff_amt = abs(price_diff)

        trade_off = (
            f"{more_expensive.get('name')} costs ${diff_amt:.2f} more than {cheaper.get('name')}. "
            f"In exchange, it offers a reliability score of {more_expensive.get('reliability_score')}/10 "
            f"(vs {cheaper.get('reliability_score')}/10) and features: "
            f"{', '.join(more_expensive.get('features', [])[:2])}."
        )
        return trade_off

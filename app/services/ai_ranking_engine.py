"""
PayPilot AI - Multi-Constraint AI Product Ranking Engine
Module Owner: Shubhneet

Implements deterministic multi-objective ranking algorithms across products
and multi-item bundles:
- Evaluates combination search space (Cartesian product of categories)
- Scores bundles based on user priority weights (reliability, cost headroom, delivery speed, warranty)
- Synthesizes:
  * Recommended Bundle (optimal balance under stated budget)
  * Budget-Saver Bundle (minimum expenditure)
  * Premium / Max-Reliability Bundle (unconstrained quality benchmark)
  * Emergency Urgency Bundle (turnaround and warranty focus)
"""

import itertools
from typing import List, Dict, Any, Optional
from app.models import Product
from app.services.catalogue_service import CatalogueService
from app.services.budget_guard import BudgetGuardService


class AIRankingEngine:
    """
    Multi-constraint reasoning engine for shopping optimization.
    """

    @classmethod
    def score_product(
        cls,
        product: Product,
        weights: Dict[str, float],
        max_price_ref: float = 100.0
    ) -> float:
        """
        Computes a normalized multi-factor composite score [0.0 - 100.0] for an individual product.
        """
        # 1. Reliability score: [0 - 10] -> [0 - 100]
        rel_norm = (product.reliability_score / 10.0) * 100.0

        # 2. Cost score: inverse normalized to price reference [0 - 100]
        price = max(product.price, 1.0)
        cost_norm = max(0.0, min(100.0, (1.0 - (price / max_price_ref)) * 100.0))

        # 3. Delivery speed score: 1 day = 100, 2 days = 70, 3+ days = 40
        delivery_map = {1: 100.0, 2: 70.0, 3: 40.0}
        del_norm = delivery_map.get(product.delivery_days, 30.0)

        # 4. Warranty score: 36mo = 100, 24mo = 80, 12mo = 50, <12mo = 20
        war_norm = min(100.0, (product.warranty_months / 36.0) * 100.0)

        # Weighted composite
        composite = (
            weights.get("reliability", 0.55) * rel_norm +
            weights.get("cost", 0.25) * cost_norm +
            weights.get("delivery_speed", 0.10) * del_norm +
            weights.get("warranty", 0.10) * war_norm
        )
        return round(composite, 2)

    @classmethod
    def rank_products_in_category(
        cls,
        category: str,
        weights: Dict[str, float],
        max_budget: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves and ranks all products in a given category based on weights.
        """
        products = CatalogueService.get_all_products(category=category)
        if not products:
            return []

        max_price = max((p.price for p in products), default=100.0)
        ranked = []
        for p in products:
            score = cls.score_product(p, weights, max_price_ref=max_price)
            within_cap = (p.price <= max_budget) if max_budget else True
            ranked.append({
                "product": p,
                "score": score,
                "is_within_budget_cap": within_cap,
                "price": p.price,
                "reliability": p.reliability_score,
                "delivery_days": p.delivery_days,
                "warranty_months": p.warranty_months
            })

        # Sort descending by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked

    @classmethod
    def optimize_multi_item_bundle(
        cls,
        categories: List[str],
        stated_budget: float,
        priority: str = "reliability",
        weights: Optional[Dict[str, float]] = None,
        apply_tax: bool = False,
        apply_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates full Cartesian combination space across requested categories
        and determines optimal bundles satisfying the user's constraints.
        """
        stated_budget = round(float(stated_budget), 2)

        # Standard weights if not provided
        if not weights:
            weight_maps = {
                "reliability": {"reliability": 0.55, "cost": 0.25, "delivery_speed": 0.10, "warranty": 0.10},
                "cost": {"reliability": 0.20, "cost": 0.65, "delivery_speed": 0.075, "warranty": 0.075},
                "delivery_speed": {"reliability": 0.30, "cost": 0.20, "delivery_speed": 0.40, "warranty": 0.10},
                "warranty": {"reliability": 0.35, "cost": 0.20, "delivery_speed": 0.10, "warranty": 0.35}
            }
            weights = weight_maps.get(priority, weight_maps["reliability"])

        # Fetch products per category
        category_products: Dict[str, List[Product]] = {}
        for cat in categories:
            items = CatalogueService.get_all_products(category=cat)
            if not items:
                return {
                    "error": f"No catalogue products found for category '{cat}'",
                    "missing_category": cat,
                    "available_categories": CatalogueService.get_categories()
                }
            category_products[cat] = items

        # Compute max price across all products for normalization
        all_prods = [p for prods in category_products.values() for p in prods]
        max_cat_price = max((p.price for p in all_prods), default=100.0)

        # Cartesian product combinations (1 per category)
        prod_lists = [category_products[cat] for cat in categories]
        all_combinations = list(itertools.product(*prod_lists))

        evaluated_bundles = []
        for combo in all_combinations:
            combo_list = list(combo)
            totals = BudgetGuardService.calculate_totals(
                combo_list,
                apply_tax=apply_tax,
                apply_shipping=apply_shipping
            )
            total_cost = totals["total"]
            subtotal = totals["subtotal"]

            # Compute bundle metrics
            avg_reliability = round(sum(p.reliability_score for p in combo_list) / len(combo_list), 2)
            max_delivery_days = max(p.delivery_days for p in combo_list)
            avg_warranty = round(sum(p.warranty_months for p in combo_list) / len(combo_list), 1)

            # Individual scores
            item_scores = [cls.score_product(p, weights, max_cat_price) for p in combo_list]
            avg_composite_score = round(sum(item_scores) / len(item_scores), 2)

            is_within = total_cost <= stated_budget
            surplus = round(stated_budget - total_cost, 2) if is_within else 0.0
            shortfall = round(total_cost - stated_budget, 2) if not is_within else 0.0

            # Composite multi-objective score including budget fitness
            budget_fitness = max(0.0, 1.0 - (total_cost / stated_budget)) if stated_budget > 0 else 0.0
            bundle_score = round((avg_composite_score * 0.70) + (budget_fitness * 30.0 if is_within else -50.0), 2)

            evaluated_bundles.append({
                "items": combo_list,
                "item_dicts": [p.to_dict() for p in combo_list],
                "subtotal": subtotal,
                "total_cost": total_cost,
                "totals_breakdown": totals,
                "average_reliability": avg_reliability,
                "max_delivery_days": max_delivery_days,
                "average_warranty_months": avg_warranty,
                "composite_score": bundle_score,
                "is_within_budget": is_within,
                "surplus": surplus,
                "shortfall": shortfall,
                "utilization_pct": round((total_cost / stated_budget) * 100, 1) if stated_budget > 0 else 0.0
            })

        # Separate within-budget from over-budget
        within_budget = [b for b in evaluated_bundles if b["is_within_budget"]]

        # 1. Budget-Saver Bundle (lowest total cost)
        budget_saver = min(
            within_budget if within_budget else evaluated_bundles,
            key=lambda b: b["total_cost"]
        )

        # 2. Recommended Bundle:
        # Highest composite score strictly within budget
        if within_budget:
            if priority == "cost":
                recommended = budget_saver
            elif priority == "delivery_speed":
                # Sort by delivery turnaround ascending, then reliability descending
                recommended = sorted(
                    within_budget,
                    key=lambda b: (b["max_delivery_days"], -b["average_reliability"], b["total_cost"])
                )[0]
            elif priority == "warranty":
                recommended = sorted(
                    within_budget,
                    key=lambda b: (-b["average_warranty_months"], -b["average_reliability"], b["total_cost"])
                )[0]
            else:  # reliability
                recommended = sorted(
                    within_budget,
                    key=lambda b: (-b["average_reliability"], -b["composite_score"], b["total_cost"])
                )[0]
        else:
            recommended = None

        # 3. Premium / Maximum Reliability Bundle (unconstrained quality)
        premium_bundle = sorted(
            evaluated_bundles,
            key=lambda b: (-b["average_reliability"], b["total_cost"])
        )[0]

        # 4. Emergency Fast-Delivery Bundle
        fast_bundle = sorted(
            within_budget if within_budget else evaluated_bundles,
            key=lambda b: (b["max_delivery_days"], -b["average_reliability"], b["total_cost"])
        )[0]

        return {
            "status": "success",
            "stated_budget": stated_budget,
            "priority": priority,
            "total_combinations_evaluated": len(evaluated_bundles),
            "feasible_combinations_count": len(within_budget),
            "has_feasible_solution": len(within_budget) > 0,
            "recommended_bundle": recommended,
            "budget_saver_bundle": budget_saver,
            "premium_bundle": premium_bundle,
            "fast_bundle": fast_bundle,
            "category_products": {cat: [p.to_dict() for p in prods] for cat, prods in category_products.items()}
        }

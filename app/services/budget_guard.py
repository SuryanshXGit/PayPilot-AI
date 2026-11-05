import itertools
from typing import List, Dict, Any, Optional
from app.services.catalogue_service import CatalogueService
from app.models import Product


class BudgetGuardService:
    """
    Deterministic budget verification and bundle optimization engine.
    Ensures zero-hallucination calculations using verified catalogue prices.
    """

    DEFAULT_TAX_RATE = 0.08  # 8% estimated standard sales tax
    FREE_SHIPPING_THRESHOLD = 35.00
    STANDARD_SHIPPING_FEE = 4.99

    @staticmethod
    def calculate_totals(
        products: List[Product],
        apply_tax: bool = False,
        apply_shipping: bool = False,
        tax_rate: float = DEFAULT_TAX_RATE
    ) -> Dict[str, float]:
        """
        Pure deterministic arithmetic calculation.
        """
        subtotal = round(sum(p.price for p in products), 2)

        tax = 0.0
        if apply_tax:
            tax = round(subtotal * tax_rate, 2)

        shipping = 0.0
        if apply_shipping:
            if subtotal > 0 and subtotal < BudgetGuardService.FREE_SHIPPING_THRESHOLD:
                shipping = BudgetGuardService.STANDARD_SHIPPING_FEE
            else:
                shipping = 0.0

        total = round(subtotal + tax + shipping, 2)

        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total
        }

    @staticmethod
    def check_bundle(
        item_ids: List[str],
        stated_budget: float,
        apply_tax: bool = False,
        apply_shipping: bool = False,
        include_bills: bool = False,
        bills_due_within_days: int = 7
    ) -> Dict[str, Any]:
        """
        Validate an item list against user's stated budget.
        Checks known catalogue prices, flags over-budget status,
        and optionally factors in upcoming bill commitments.
        """
        stated_budget = round(float(stated_budget), 2)
        products = CatalogueService.get_products_by_ids(item_ids)

        found_ids = {p.id for p in products}
        missing_ids = [pid for pid in item_ids if pid not in found_ids]

        totals = BudgetGuardService.calculate_totals(
            products=products,
            apply_tax=apply_tax,
            apply_shipping=apply_shipping
        )

        total_cost = totals["total"]
        difference = round(stated_budget - total_cost, 2)
        is_over = total_cost > stated_budget

        if is_over:
            status = "OVER_BUDGET"
            status_message = (
                f"Bundle total ${total_cost:.2f} exceeds your ${stated_budget:.2f} budget "
                f"by ${abs(difference):.2f}."
            )
        elif difference == 0:
            status = "AT_BUDGET"
            status_message = f"Bundle total ${total_cost:.2f} matches your exact budget."
        else:
            status = "UNDER_BUDGET"
            status_message = (
                f"Bundle total ${total_cost:.2f} is within budget. "
                f"You have ${difference:.2f} remaining."
            )

        utilization_pct = round((total_cost / stated_budget) * 100, 1) if stated_budget > 0 else 0.0

        # Average reliability
        avg_reliability = (
            round(sum(p.reliability_score for p in products) / len(products), 2)
            if products else 0.0
        )

        response: Dict[str, Any] = {
            "stated_budget": stated_budget,
            "currency": "USD",
            "calculation_basis": "deterministic_catalogue_lookup",
            "pricing_breakdown": totals,
            "status": status,
            "is_over_budget": is_over,
            "difference": difference,
            "amount_over": round(abs(difference), 2) if is_over else 0.0,
            "amount_remaining": difference if not is_over else 0.0,
            "budget_utilization_percentage": utilization_pct,
            "average_reliability_score": avg_reliability,
            "status_message": status_message,
            "items_count": len(products),
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "brand": p.brand,
                    "price": p.price,
                    "reliability_score": p.reliability_score,
                    "warranty_months": p.warranty_months,
                    "delivery_days": p.delivery_days,
                    "data_source": p.data_source,
                    "data_source_label": p.data_source_label
                }
                for p in products
            ],
            "missing_item_ids": missing_ids
        }

        # Bill impact check if requested (Proactive Financial Health)
        if include_bills:
            from app.services.bill_service import BillService
            bills_summary = BillService.get_financial_health_summary(
                stated_shopping_budget=stated_budget,
                days_window=bills_due_within_days
            )
            upcoming_bills_total = bills_summary["upcoming_bills_total"]
            analysis = bills_summary.get("shopping_budget_analysis", {})
            disposable_budget = analysis.get("disposable_shopping_budget_after_bills", max(0.0, round(stated_budget - upcoming_bills_total, 2)))

            is_over_disposable = total_cost > disposable_budget
            disposable_diff = round(disposable_budget - total_cost, 2)

            response["bill_awareness"] = {
                "active": True,
                "days_window": bills_due_within_days,
                "upcoming_bills_total": upcoming_bills_total,
                "disposable_budget_after_bills": disposable_budget,
                "is_over_disposable_budget": is_over_disposable,
                "disposable_difference": disposable_diff,
                "upcoming_bills_count": len(bills_summary["upcoming_bills"]),
                "advisory": (
                    f"Warning: Upcoming bills (${upcoming_bills_total:.2f}) due within {bills_due_within_days} days "
                    f"leave an effective shopping balance of ${disposable_budget:.2f}."
                    if is_over_disposable else
                    f"Safe: Bundle leaves ${disposable_diff:.2f} even after covering ${upcoming_bills_total:.2f} in bills due this week."
                )
            }

        return response

    @staticmethod
    def optimize_bundle(
        categories: List[str],
        stated_budget: float,
        priority: str = "reliability",
        apply_tax: bool = False,
        apply_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        Multi-Item Budget Optimizer.
        Evaluates product options across requested categories, balances constraints,
        and generates:
        1. Best recommended bundle staying within budget.
        2. Budget saver bundle (minimum cost).
        3. High-performance/premium bundle (with clear over-budget flag if over).
        4. Trade-off explanations.
        """
        stated_budget = round(float(stated_budget), 2)
        category_products: Dict[str, List[Product]] = {}

        for cat in categories:
            items = CatalogueService.get_all_products(category=cat)
            if not items:
                return {
                    "error": f"No catalogue products found for category '{cat}'",
                    "missing_category": cat
                }
            category_products[cat] = items

        # Generate combinations (1 item per category)
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
            cost = totals["total"]
            avg_reliability = sum(p.reliability_score for p in combo_list) / len(combo_list)
            is_under = cost <= stated_budget

            evaluated_bundles.append({
                "items": combo_list,
                "subtotal": totals["subtotal"],
                "total": cost,
                "totals_breakdown": totals,
                "average_reliability": round(avg_reliability, 2),
                "is_within_budget": is_under,
                "surplus": round(stated_budget - cost, 2) if is_under else 0.0,
                "shortfall": round(cost - stated_budget, 2) if not is_under else 0.0
            })

        # Filter within-budget bundles
        within_budget = [b for b in evaluated_bundles if b["is_within_budget"]]

        # 1. Budget Saver (lowest price within budget, or lowest price overall if none)
        budget_saver = min(within_budget if within_budget else evaluated_bundles, key=lambda b: b["total"])

        # 2. Recommended Bundle (prioritize reliability within budget)
        if within_budget:
            if priority == "reliability":
                # Sort primarily by average reliability descending, then lowest price
                recommended = sorted(
                    within_budget,
                    key=lambda b: (-b["average_reliability"], b["total"])
                )[0]
            elif priority == "cost":
                recommended = budget_saver
            else:  # balanced: score = reliability / cost normalized
                recommended = sorted(
                    within_budget,
                    key=lambda b: (-(b["average_reliability"] * 100 / b["total"]))
                )[0]
        else:
            recommended = None

        # 3. Premium / Maximum Reliability Bundle (highest reliability overall)
        premium_overall = sorted(
            evaluated_bundles,
            key=lambda b: (-b["average_reliability"], b["total"])
        )[0]

        # Generate trade-off explanations
        explanations = []
        if recommended:
            explanations.append(
                f"Selected optimal bundle staying strictly under ${stated_budget:.2f}. "
                f"Total ${recommended['total']:.2f} leaves ${recommended['surplus']:.2f} surplus "
                f"with an average reliability rating of {recommended['average_reliability']}/10."
            )
            # Itemize trade-offs
            for item in recommended["items"]:
                # Compare against higher or lower options in the same category
                cat_items = category_products[item.category]
                cheaper = [p for p in cat_items if p.price < item.price]
                pricier = [p for p in cat_items if p.price > item.price]

                if pricier:
                    next_up = min(pricier, key=lambda p: p.price)
                    explanations.append(
                        f"In {item.category.replace('_', ' ').title()}: "
                        f"Chose '{item.name}' (${item.price:.2f}, {item.reliability_score}/10) over '{next_up.name}' (${next_up.price:.2f}) "
                        f"saving ${next_up.price - item.price:.2f} to protect the bundle budget."
                    )
                elif cheaper:
                    cheapest = min(cheaper, key=lambda p: p.price)
                    explanations.append(
                        f"In {item.category.replace('_', ' ').title()}: "
                        f"Invested ${item.price - cheapest.price:.2f} extra for '{item.name}' ({item.reliability_score}/10 vs {cheapest.reliability_score}/10) "
                        f"for enhanced durability while staying under budget."
                    )
        else:
            explanations.append(
                f"No complete bundle found within ${stated_budget:.2f}. "
                f"Lowest possible bundle cost is ${budget_saver['total']:.2f} "
                f"(shortfall of ${budget_saver['shortfall']:.2f})."
            )

        def format_bundle(bundle_data, label):
            if not bundle_data:
                return None
            return {
                "label": label,
                "is_within_budget": bundle_data["is_within_budget"],
                "total_cost": bundle_data["total"],
                "totals_breakdown": bundle_data["totals_breakdown"],
                "difference": round(stated_budget - bundle_data["total"], 2),
                "average_reliability": bundle_data["average_reliability"],
                "items": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "category": p.category,
                        "brand": p.brand,
                        "price": p.price,
                        "reliability_score": p.reliability_score,
                        "warranty_months": p.warranty_months,
                        "delivery_days": p.delivery_days,
                        "data_source_label": p.data_source_label
                    }
                    for p in bundle_data["items"]
                ]
            }

        return {
            "stated_budget": stated_budget,
            "currency": "USD",
            "requested_categories": categories,
            "total_combinations_evaluated": len(evaluated_bundles),
            "feasible_combinations_count": len(within_budget),
            "recommended_bundle": format_bundle(recommended, "Best Fit (High Reliability Under Budget)"),
            "budget_saver_bundle": format_bundle(budget_saver, "Lowest Total Cost Option"),
            "premium_bundle": format_bundle(premium_overall, "Maximum Spec / Audiophile Option"),
            "trade_off_explanations": explanations
        }

    @staticmethod
    def suggest_alternatives_for_over_budget(
        current_item_ids: List[str],
        stated_budget: float,
        apply_tax: bool = False,
        apply_shipping: bool = False
    ) -> Dict[str, Any]:
        """
        When a user's chosen bundle is over budget, deterministically calculate
        which item swaps will bring the bundle under budget while preserving items.
        """
        stated_budget = round(float(stated_budget), 2)
        current_products = CatalogueService.get_products_by_ids(current_item_ids)

        current_totals = BudgetGuardService.calculate_totals(
            current_products,
            apply_tax=apply_tax,
            apply_shipping=apply_shipping
        )
        current_cost = current_totals["total"]

        if current_cost <= stated_budget:
            return {
                "is_over_budget": False,
                "current_cost": current_cost,
                "stated_budget": stated_budget,
                "message": "Current bundle is already within budget. No alternatives needed."
            }

        shortfall = round(current_cost - stated_budget, 2)
        suggestions = []

        # Analyze single-item swaps
        for i, current_p in enumerate(current_products):
            # Fetch alternatives in same category
            cat_candidates = CatalogueService.get_all_products(category=current_p.category)
            for candidate in cat_candidates:
                if candidate.id == current_p.id:
                    continue
                # Calculate bundle if replaced
                trial_products = list(current_products)
                trial_products[i] = candidate

                trial_totals = BudgetGuardService.calculate_totals(
                    trial_products,
                    apply_tax=apply_tax,
                    apply_shipping=apply_shipping
                )
                trial_cost = trial_totals["total"]
                savings = round(current_cost - trial_cost, 2)

                if trial_cost <= stated_budget:
                    surplus = round(stated_budget - trial_cost, 2)
                    suggestions.append({
                        "type": "single_item_swap",
                        "remove_item": {
                            "id": current_p.id,
                            "name": current_p.name,
                            "price": current_p.price,
                            "reliability_score": current_p.reliability_score
                        },
                        "add_item": {
                            "id": candidate.id,
                            "name": candidate.name,
                            "price": candidate.price,
                            "reliability_score": candidate.reliability_score
                        },
                        "savings": savings,
                        "new_bundle_total": trial_cost,
                        "new_surplus": surplus,
                        "trade_off_explanation": (
                            f"Swap '{current_p.name}' (${current_p.price:.2f}) for '{candidate.name}' (${candidate.price:.2f}). "
                            f"Saves ${savings:.2f}, bringing total down to ${trial_cost:.2f} (${surplus:.2f} under budget). "
                            f"Reliability adjusts from {current_p.reliability_score} to {candidate.reliability_score}."
                        )
                    })

        # Sort suggestions by highest reliability retained, then largest savings
        suggestions = sorted(
            suggestions,
            key=lambda s: (-s["add_item"]["reliability_score"], -s["savings"])
        )

        return {
            "is_over_budget": True,
            "current_cost": current_cost,
            "stated_budget": stated_budget,
            "shortfall": shortfall,
            "message": f"Bundle exceeds budget by ${shortfall:.2f}. Found {len(suggestions)} viable swap alternative(s).",
            "viable_swaps": suggestions
        }

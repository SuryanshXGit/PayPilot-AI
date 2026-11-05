"""
budget_guard.py - Deterministic Budget Verification & Guard Engine
Owned by Sehaj (Product Data, Comparison & Testing Lead) / Jaskaran (Flask Backend & Budget Guard)

Core Principles:
1. Deterministic arithmetic: NEVER let an LLM hallucinate financial totals or hide shortfalls.
2. Independent verification: Calculate item totals, shipping, and taxes using known catalogue values.
3. Over-budget flagging: Proactively flag bundles exceeding max_budget and suggest deterministic alternatives.
4. Compliance: Never treat a Pay in 4 installment as proof of affordability; always show full purchase total.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP


class BudgetGuard:
    @staticmethod
    def _to_decimal(val: float) -> Decimal:
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def calculate_basket_total(
        cls,
        items: List[Dict[str, Any]],
        shipping_cost: float = 0.00,
        tax_rate: float = 0.00
    ) -> Dict[str, Any]:
        """
        Calculate total deterministically using Decimal to avoid floating point precision artifacts.
        """
        item_subtotal = Decimal("0.00")
        item_breakdown = []

        for item in items:
            name = item.get("name", "Unknown Item")
            price_dec = cls._to_decimal(item.get("price", 0.00))
            qty = int(item.get("quantity", 1))
            line_total = price_dec * qty
            item_subtotal += line_total
            item_breakdown.append({
                "id": item.get("id"),
                "name": name,
                "unit_price": float(price_dec),
                "quantity": qty,
                "line_total": float(line_total)
            })

        shipping_dec = cls._to_decimal(shipping_cost)
        tax_dec = (item_subtotal * cls._to_decimal(tax_rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        grand_total = item_subtotal + shipping_dec + tax_dec

        return {
            "subtotal": float(item_subtotal),
            "shipping": float(shipping_dec),
            "tax": float(tax_dec),
            "grand_total": float(grand_total),
            "item_breakdown": item_breakdown,
            "currency": "USD"
        }

    @classmethod
    def evaluate_budget(
        cls,
        items: List[Dict[str, Any]],
        max_budget: float,
        shipping_cost: float = 0.00,
        tax_rate: float = 0.00,
        upcoming_bills_7_days: float = 0.00
    ) -> Dict[str, Any]:
        """
        Deterministically evaluates if basket conforms to stated maximum budget.
        Flags over-budget combinations and reports exact difference.
        """
        totals = cls.calculate_basket_total(items, shipping_cost, tax_rate)
        grand_total_dec = cls._to_decimal(totals["grand_total"])
        budget_dec = cls._to_decimal(max_budget)
        bills_dec = cls._to_decimal(upcoming_bills_7_days)

        difference = budget_dec - grand_total_dec
        is_under_budget = difference >= Decimal("0.00")

        # Proactive Financial Health Check: Basket + Upcoming 7-Day Bills
        total_immediate_commitments = grand_total_dec + bills_dec

        flags = []
        status = "APPROVED" if is_under_budget else "OVER_BUDGET"

        if not is_under_budget:
            over_amount = abs(difference)
            pct_over = (over_amount / budget_dec) * Decimal("100.0")
            flags.append(
                f"BUDGET EXCEEDED: Cart total (${grand_total_dec}) exceeds limit (${budget_dec}) "
                f"by ${over_amount} ({pct_over:.1f}% over budget)."
            )

        if bills_dec > Decimal("0.00"):
            flags.append(
                f"UPCOMING BILLS NOTICE: You have ${bills_dec} in bills due within 7 days. "
                f"Combined immediate outlay is ${total_immediate_commitments}."
            )

        return {
            "status": status,
            "is_under_budget": is_under_budget,
            "max_budget": float(budget_dec),
            "grand_total": float(grand_total_dec),
            "variance": float(difference),
            "upcoming_bills_7_days": float(bills_dec),
            "total_immediate_commitments": float(total_immediate_commitments),
            "flags": flags,
            "totals": totals
        }

    @classmethod
    def suggest_alternative_substitutions(
        cls,
        selected_items: List[Dict[str, Any]],
        catalogue_items: List[Dict[str, Any]],
        max_budget: float
    ) -> List[Dict[str, Any]]:
        """
        Deterministic substitution engine:
        If a bundle is over budget, finds lower-priced alternatives in the same category
        to bring the overall basket under max_budget.
        """
        eval_result = cls.evaluate_budget(selected_items, max_budget)
        if eval_result["is_under_budget"]:
            return []  # No substitution needed

        suggestions = []
        budget_dec = cls._to_decimal(max_budget)

        for idx, item in enumerate(selected_items):
            cat = item.get("category")
            curr_price = cls._to_decimal(item.get("price", 0))

            # Look for items in the same category with lower price
            candidates = [
                c for c in catalogue_items
                if c.get("category") == cat and cls._to_decimal(c.get("price", 0)) < curr_price
            ]
            # Sort candidates by reliability descending
            candidates.sort(key=lambda x: x.get("reliability_score", 0), reverse=True)

            for candidate in candidates:
                # Test replacing item with candidate
                tentative_basket = list(selected_items)
                tentative_basket[idx] = candidate
                tentative_eval = cls.evaluate_budget(tentative_basket, max_budget)

                if tentative_eval["is_under_budget"]:
                    suggestions.append({
                        "replace_item_id": item.get("id"),
                        "replace_item_name": item.get("name"),
                        "replace_price": float(curr_price),
                        "suggested_item_id": candidate.get("id"),
                        "suggested_item_name": candidate.get("name"),
                        "suggested_price": candidate.get("price"),
                        "new_bundle_total": tentative_eval["grand_total"],
                        "new_savings_under_budget": tentative_eval["variance"],
                        "reliability_difference": candidate.get("reliability_score", 0) - item.get("reliability_score", 0),
                        "rationale": f"Swap {item.get('name')} for {candidate.get('name')} to satisfy $150 budget limit."
                    })

        return suggestions

    @staticmethod
    def validate_pay_in_4_compliance(text: str) -> Dict[str, Any]:
        """
        Validates hackathon guardrail:
        - Do not claim PayPal Pay in 4 is always available.
        - Must mention eligibility or subject to credit approval.
        """
        text_lower = text.lower()
        has_pay_in_4 = "pay in 4" in text_lower or "pay-in-4" in text_lower or "installment" in text_lower
        if not has_pay_in_4:
            return {"compliant": True, "notes": "No installment claim made"}

        # Check required qualifiers
        qualifiers = ["eligibility", "eligible", "subject to", "terms apply", "circumstances", "if approved"]
        has_qualifier = any(q in text_lower for q in qualifiers)

        # Check forbidden absolute guarantees
        absolutes = ["always available", "guaranteed", "no credit check", "everyone gets"]
        has_forbidden_absolute = any(a in text_lower for a in absolutes)

        compliant = has_qualifier and not has_forbidden_absolute

        return {
            "compliant": compliant,
            "has_pay_in_4_reference": True,
            "has_proper_qualifier": has_qualifier,
            "has_forbidden_absolute": has_forbidden_absolute,
            "guardrail_status": "PASS" if compliant else "FAIL - Violates PayPal Pay in 4 accuracy guardrail"
        }

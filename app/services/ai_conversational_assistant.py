"""
PayPilot AI - Conversational Shopping Assistant (Idea 05)
Module Owner: Shubhneet

Implements an intelligent multi-turn conversational AI shopping assistant:
- Maintains dialogue state (active items, stated budget, active priorities, history)
- Interprets user adjustments ("Make it cheaper", "What if budget is $120?", "Why not BenQ?")
- Synthesizes natural dialogue responses paired with deterministic Budget Guard calculations
- Strictly adheres to PayPal Pay in 4 disclosures and payment verification guardrails
"""

from typing import Dict, Any, List, Optional
from app.models import Product
from app.services.ai_intent_parser import AIIntentParser
from app.services.ai_ranking_engine import AIRankingEngine
from app.services.ai_tradeoff_explainer import AITradeOffExplainer
from app.services.catalogue_service import CatalogueService
from app.services.budget_guard import BudgetGuardService


class AIConversationalAssistant:
    """
    Multi-turn conversational chatbot for budget-conscious shopping.
    """

    def __init__(self):
        # In-memory session store: session_id -> state dict
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """Retrieves or initializes session dialogue state."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "session_id": session_id,
                "history": [],
                "stated_budget": 150.0,
                "priority": "reliability",
                "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
                "active_bundle": None,
                "active_items": [],
                "context": "college_dorm"
            }
        return self._sessions[session_id]

    def reset_session(self, session_id: str):
        """Resets dialogue state for a clean demo run."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def process_message(
        self,
        session_id: str,
        user_message: str,
        override_budget: Optional[float] = None,
        override_priority: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes a user message in conversation, updating state and returning
        conversational text along with structured recommendation data.
        """
        session = self.get_or_create_session(session_id)
        msg_clean = user_message.strip()
        msg_lower = msg_clean.lower()

        # 1. Parse intent from message
        parsed = AIIntentParser.parse(msg_clean)

        # 2. Update state from overrides or parsed parameters
        if override_budget is not None:
            session["stated_budget"] = float(override_budget)
        elif parsed["stated_budget"] is not None:
            session["stated_budget"] = float(parsed["stated_budget"])

        if override_priority is not None:
            session["priority"] = override_priority
        elif parsed["priority"] and parsed["intent_type"] != "TRADE_OFF_QUERY":
            session["priority"] = parsed["priority"]

        if parsed["categories"] and parsed["intent_type"] not in ["TRADE_OFF_QUERY", "GENERAL_INQUIRY"]:
            session["categories"] = parsed["categories"]

        if parsed["context"] != "general_shopping":
            session["context"] = parsed["context"]

        # Record user utterance in history
        session["history"].append({"sender": "user", "text": msg_clean})

        # 3. Route conversational response based on intent classification
        intent = parsed["intent_type"]

        response_payload = self._generate_response(
            session=session,
            parsed=parsed,
            user_message=msg_clean,
            msg_lower=msg_lower,
            intent=intent
        )

        # Record assistant reply in history
        session["history"].append({
            "sender": "assistant",
            "text": response_payload["reply_text"],
            "bundle_total": response_payload.get("bundle", {}).get("total_cost") if response_payload.get("bundle") else None
        })

        return response_payload

    def _generate_response(
        self,
        session: Dict[str, Any],
        parsed: Dict[str, Any],
        user_message: str,
        msg_lower: str,
        intent: str
    ) -> Dict[str, Any]:
        """Dispatches logic for different conversation intents."""

        # A. Check for PayPal Pay in 4 questions
        if any(w in msg_lower for w in ["pay in 4", "installment", "pay in four", "financing", "monthly payment"]):
            return self._handle_pay_in_4_inquiry(session)

        # B. Check for trade-off queries (e.g. "Why did you pick TaoTronics over BenQ?")
        if intent == "TRADE_OFF_QUERY" or "why" in msg_lower:
            return self._handle_tradeoff_query(session, msg_lower)

        # C. Check for swap requests (e.g. "Swap the lamp to BenQ" or "Change to cheaper steamer")
        if intent == "SWAP_REQUEST":
            return self._handle_swap_request(session, parsed, msg_lower)

        # D. Check for checkout queries (e.g. "Proceed to checkout", "Buy now")
        if intent == "CHECKOUT_INTENT":
            return self._handle_checkout_intent(session)

        # E. Multi-item optimization / Budget adjustment / General query
        return self._handle_bundle_optimization(session, parsed, intent)

    def _handle_bundle_optimization(
        self,
        session: Dict[str, Any],
        parsed: Dict[str, Any],
        intent: str
    ) -> Dict[str, Any]:
        """Runs the optimization engine and constructs assistant reply."""
        categories = session["categories"]
        budget = session["stated_budget"]
        priority = session["priority"]

        # Run ranking engine
        opt_res = AIRankingEngine.optimize_multi_item_bundle(
            categories=categories,
            stated_budget=budget,
            priority=priority
        )

        rec_bundle = opt_res["recommended_bundle"]
        saver_bundle = opt_res["budget_saver_bundle"]
        prem_bundle = opt_res["premium_bundle"]

        session["active_bundle"] = rec_bundle
        if rec_bundle:
            session["active_items"] = [item.id for item in rec_bundle["items"]]

        # Generate trade-off explanations
        explanations = AITradeOffExplainer.explain_bundle_recommendation(
            recommended_bundle=rec_bundle,
            budget_saver_bundle=saver_bundle,
            premium_bundle=prem_bundle,
            stated_budget=budget,
            priority=priority,
            category_products=opt_res["category_products"]
        )

        if rec_bundle:
            items_str = ", ".join(f"{it.name} (${it.price:.2f})" for it in rec_bundle["items"])
            reply_text = (
                f"I've optimized your basket across {len(categories)} categories within your ${budget:.2f} budget "
                f"prioritizing **{priority.replace('_', ' ').title()}**.\n\n"
                f"**Recommended Selection:**\n"
                f"• {chr(10).join(['- ' + it.name + ' ($' + f'{it.price:.2f}' + ' | ★ ' + str(it.reliability_score) + '/10)' for it in rec_bundle['items']])}\n\n"
                f"**Financial Check (Budget Guard):**\n"
                f"• Bundle Total: **${rec_bundle['total_cost']:.2f}** (Budget: ${budget:.2f})\n"
                f"• Surplus Buffer: **+${rec_bundle['surplus']:.2f} remaining**\n"
                f"• Average Reliability: **{rec_bundle['average_reliability']}/10**\n\n"
                f"Would you like me to explain any specific item trade-off, test a different budget, or proceed toward checkout?"
            )
            suggested_actions = [
                "Explain lamp trade-off",
                "What if budget is $120?",
                "Show budget-saver option",
                "Proceed to checkout"
            ]
        else:
            min_cost = saver_bundle["total_cost"]
            shortfall = round(min_cost - budget, 2)
            reply_text = (
                f"Under your current **${budget:.2f}** limit, no combination of items across the requested categories can be purchased.\n\n"
                f"The lowest-cost viable combination costs **${min_cost:.2f}**, which leaves a shortfall of **${shortfall:.2f}**.\n\n"
                f"You can increase your budget by ${shortfall:.2f} or swap an item to continue."
            )
            suggested_actions = [
                f"Increase budget to ${min_cost:.2f}",
                "Show cheapest bundle",
                "Remove one item"
            ]

        return {
            "reply_text": reply_text,
            "intent": intent,
            "budget": budget,
            "priority": priority,
            "bundle": rec_bundle,
            "budget_saver_bundle": saver_bundle,
            "premium_bundle": prem_bundle,
            "explanations": explanations,
            "suggested_actions": suggested_actions
        }

    def _handle_tradeoff_query(self, session: Dict[str, Any], msg_lower: str) -> Dict[str, Any]:
        """Provides in-depth answers explaining why specific products were chosen."""
        budget = session["stated_budget"]

        # Check for specific item queries
        if "benq" in msg_lower or "lamp" in msg_lower:
            reply_text = (
                f"**Trade-Off Breakdown — Desk Lamp Selection:**\n\n"
                f"We chose the **TaoTronics Eye-Care Multi-Spectrum Lamp** ($32.99, ★ 9.2/10) over the "
                f"**BenQ e-Reading Architectural Task Light** ($89.00, ★ 9.6/10).\n\n"
                f"• **Budget Protection**: BenQ costs $89.00 — consuming nearly 60% of your total $150.00 budget. "
                f"Choosing TaoTronics saves **$56.01**, which provides the financial headroom needed to include "
                f"both a turbo garment steamer ($44.99) and active noise-cancelling study earbuds ($59.99).\n"
                f"• **Reliability Trade-off**: You only compromise 0.4 pts in reliability (9.2 vs 9.6) while still "
                f"getting 5 color temperatures, flicker-free diffusion, multi-angle folding, and a 24-month warranty."
            )
        elif "earbud" in msg_lower or "sony" in msg_lower or "buds" in msg_lower:
            reply_text = (
                f"**Trade-Off Breakdown — Study Earbuds Selection:**\n\n"
                f"We selected the **Anker Soundcore Space A40** ($59.99, ★ 9.4/10) over flagship studio earbuds.\n\n"
                f"• **Budget Safeguard**: Premium earbuds like Sony WF-1000XM5 retail around $149+, which would single-handedly exhaust your entire $150 budget.\n"
                f"• **Feature Parity**: Anker Space A40 delivers adaptive active noise cancellation (ANC), 50-hour total battery life, and Hi-Res wireless audio at a fraction of the cost."
            )
        else:
            reply_text = (
                f"Every item in your PayPilot recommendation is selected using deterministic mathematical trade-offs:\n"
                f"1. Items are picked to maximize reliability score while strictly honoring your ${budget:.2f} cap.\n"
                f"2. Premium items with excessive price tags are avoided when high-reliability alternatives provide 95%+ of the utility at a fraction of the price."
            )

        return {
            "reply_text": reply_text,
            "intent": "TRADE_OFF_QUERY",
            "budget": session["stated_budget"],
            "bundle": session.get("active_bundle"),
            "suggested_actions": [
                "Can you make it cheaper?",
                "What if my budget is $180?",
                "Proceed to checkout"
            ]
        }

    def _handle_swap_request(
        self,
        session: Dict[str, Any],
        parsed: Dict[str, Any],
        msg_lower: str
    ) -> Dict[str, Any]:
        """Handles user requests to swap an item in their active bundle."""
        budget = session["stated_budget"]
        active_bundle = session.get("active_bundle")

        if not active_bundle:
            return self._handle_bundle_optimization(session, parsed, "SWAP_REQUEST")

        current_items = list(active_bundle["items"])

        # Determine target category to swap
        target_cat = None
        if "lamp" in msg_lower:
            target_cat = "desk_lamp"
        elif "steamer" in msg_lower:
            target_cat = "portable_steamer"
        elif "earbud" in msg_lower or "bud" in msg_lower:
            target_cat = "noise_cancelling_earbuds"

        if target_cat:
            cat_products = CatalogueService.get_all_products(category=target_cat)
            current_item = next((it for it in current_items if it.category == target_cat), None)

            # Check if user wants cheaper or specific item
            if "cheaper" in msg_lower or "cheap" in msg_lower:
                candidates = [p for p in cat_products if p.price < current_item.price]
                replacement = min(candidates, key=lambda x: x.price) if candidates else None
            elif "benq" in msg_lower:
                replacement = next((p for p in cat_products if "benq" in p.name.lower()), None)
            else:
                candidates = [p for p in cat_products if p.id != current_item.id]
                replacement = candidates[0] if candidates else None

            if replacement and current_item:
                # Calculate new bundle
                new_items = [replacement if it.category == target_cat else it for it in current_items]
                totals = BudgetGuardService.calculate_totals(new_items)
                new_cost = totals["total"]
                is_within = new_cost <= budget
                surplus = round(budget - new_cost, 2) if is_within else 0.0
                shortfall = round(new_cost - budget, 2) if not is_within else 0.0

                updated_bundle = {
                    "items": new_items,
                    "item_dicts": [p.to_dict() for p in new_items],
                    "total_cost": new_cost,
                    "subtotal": totals["subtotal"],
                    "is_within_budget": is_within,
                    "surplus": surplus,
                    "shortfall": shortfall,
                    "average_reliability": round(sum(p.reliability_score for p in new_items) / len(new_items), 2)
                }
                session["active_bundle"] = updated_bundle
                session["active_items"] = [it.id for it in new_items]

                if is_within:
                    reply = (
                        f"I've updated your bundle: swapped **{current_item.name}** for **{replacement.name}** (${replacement.price:.2f}).\n\n"
                        f"• New Total: **${new_cost:.2f}**\n"
                        f"• Remaining Budget: **+${surplus:.2f}**\n"
                        f"• Average Reliability: **{updated_bundle['average_reliability']}/10**"
                    )
                else:
                    reply = (
                        f"⚠️ **Budget Guard Alert: Over Budget!**\n\n"
                        f"Swapping to **{replacement.name}** (${replacement.price:.2f}) brings your bundle to **${new_cost:.2f}**, "
                        f"which exceeds your ${budget:.2f} budget by **${shortfall:.2f}**.\n\n"
                        f"To keep this item, you will need to increase your budget by at least ${shortfall:.2f} or choose a cheaper companion item."
                    )

                return {
                    "reply_text": reply,
                    "intent": "SWAP_REQUEST",
                    "bundle": updated_bundle,
                    "suggested_actions": [
                        "Revert swap",
                        "Show alternatives",
                        "Proceed to checkout"
                    ]
                }

        return {
            "reply_text": "I can help you swap any item in your basket (lamp, steamer, or earbuds). Which item would you like to swap, or would you like to see cheaper options?",
            "intent": "SWAP_REQUEST",
            "suggested_actions": ["Swap to cheaper lamp", "Swap to cheaper steamer", "Keep current bundle"]
        }

    def _handle_pay_in_4_inquiry(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Provides compliant, honest explanations of PayPal Pay in 4."""
        bundle = session.get("active_bundle")
        total = bundle["total_cost"] if bundle else 137.97
        installment = round(total / 4.0, 2)

        reply_text = (
            f"**PayPal Pay in 4 Transparency Notice:**\n\n"
            f"If eligible, a purchase of **${total:.2f}** could be split into **4 bi-weekly payments of ~${installment:.2f}**.\n\n"
            f"🛡️ **Hackathon Accuracy & Safety Disclosures:**\n"
            f"• **Not Guaranteed**: PayPal Pay in 4 is subject to consumer eligibility and credit checks by PayPal at the time of checkout. It is never guaranteed in advance.\n"
            f"• **Affordability Guardrail**: Paying in 4 installments of ${installment:.2f} does **not** reduce your total financial liability. Your full purchase obligation remains ${total:.2f}.\n"
            f"• Actual available payment methods are confirmed directly within the PayPal Sandbox window during checkout."
        )

        return {
            "reply_text": reply_text,
            "intent": "FINANCING_INQUIRY",
            "suggested_actions": ["Check total budget", "Proceed to checkout", "View product specs"]
        }

    def _handle_checkout_intent(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Guides user toward server-locked PayPal Sandbox payment."""
        bundle = session.get("active_bundle")
        if not bundle:
            return {
                "reply_text": "Please select or optimize a product bundle before proceeding to checkout.",
                "intent": "CHECKOUT_INTENT",
                "suggested_actions": ["Optimize dorm bundle ($150)"]
            }

        total = bundle["total_cost"]
        is_within = bundle.get("is_within_budget", True)

        if not is_within:
            return {
                "reply_text": (
                    f"⚠️ **Cannot Proceed — Budget Guard Warning:**\n\n"
                    f"Your current selection totals **${total:.2f}**, which exceeds your stated limit by **${bundle.get('shortfall', 0.0):.2f}**.\n\n"
                    f"Please resolve the budget shortfall before initiating checkout."
                ),
                "intent": "CHECKOUT_INTENT",
                "suggested_actions": ["Show 1-click swap alternatives", "Adjust budget"]
            }

        reply_text = (
            f"Your order of {len(bundle['items'])} items is locked and verified with Budget Guard!\n\n"
            f"• Verified Total: **${total:.2f} USD**\n"
            f"• Average Reliability: **{bundle['average_reliability']}/10**\n\n"
            f"To initiate payment, our backend will lock the catalogue price, generate a PayPal Sandbox order, "
            f"and perform server-side cryptographic capture verification."
        )

        return {
            "reply_text": reply_text,
            "intent": "CHECKOUT_INTENT",
            "can_proceed": True,
            "checkout_data": {
                "item_ids": [it.id for it in bundle["items"]],
                "total_cost": total,
                "currency": "USD"
            },
            "suggested_actions": ["Authorize PayPal Sandbox Checkout", "Review items", "Cancel"]
        }

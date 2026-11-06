"""
PayPilot AI - AI Intent Parser
Module Owner: Jaskaran

Interprets natural language shopping requests, extracting:
- Product categories / items requested
- Stated budget constraints (strict vs flexible, exact amounts)
- User priorities (reliability, cost-savings, delivery speed, warranty)
- Contextual intent (college dorm, emergency replacement, general shopping)
- Conversational follow-ups (trade-off queries, budget adjustments, swap requests)
"""

import re
from typing import Dict, Any, List, Optional


class AIIntentParser:
    """
    Parses unstructured user text into structured shopping constraints
    and conversational intent.
    """

    # Category synonym mappings
    CATEGORY_SYNONYMS = {
        "desk_lamp": [
            "desk lamp", "lamp", "desk light", "study light", "table lamp",
            "study lamp", "reading light", "reading lamp", "led lamp", "lighting"
        ],
        "portable_steamer": [
            "portable steamer", "steamer", "garment steamer", "clothes steamer",
            "handheld steamer", "travel steamer", "fabric steamer", "iron", "steamer iron"
        ],
        "noise_cancelling_earbuds": [
            "noise-cancelling earbuds", "noise cancelling earbuds", "noise-cancelling study buds",
            "study buds", "earbuds", "ear buds", "anc earbuds", "anc buds", "headphones",
            "noise cancelling buds", "anc", "noise cancellation", "wireless earbuds", "buds"
        ],
        "laptop": [
            "laptop", "work laptop", "notebook", "computer", "pc", "thinkpad",
            "replacement laptop", "broken laptop"
        ],
        "medical_equipment": [
            "medical equipment", "medical device", "nebulizer", "blood pressure monitor",
            "glucose monitor", "health monitor", "medical bill", "urgent medical"
        ]
    }

    # Contextual keywords
    CONTEXT_KEYWORDS = {
        "college_dorm": [
            "college", "dorm", "unfurnished dorm", "moving into", "student",
            "study", "roommate", "dorm room", "campus"
        ],
        "emergency_expense": [
            "emergency", "urgent", "broken", "immediate", "replacement",
            "need today", "asap", "died", "cracked", "medical"
        ],
        "general_shopping": [
            "shopping", "buy", "purchase", "looking for", "recommend"
        ]
    }

    # Priority keywords
    PRIORITY_KEYWORDS = {
        "reliability": [
            "reliability", "reliable", "durable", "durability", "quality", "long-lasting",
            "sturdy", "trusted", "dependable", "brand reputation", "highest rated"
        ],
        "cost": [
            "cheap", "cheapest", "cost", "lowest cost", "budget saver", "save money",
            "economic", "affordable", "minimum cost", "budget friendly", "least expensive"
        ],
        "delivery_speed": [
            "fast delivery", "urgent", "1-day", "next day", "overnight", "express",
            "fast shipping", "asap", "need quickly", "quick"
        ],
        "warranty": [
            "warranty", "guarantee", "protection plan", "coverage", "24-month", "long warranty"
        ]
    }

    @classmethod
    def parse(cls, prompt: str) -> Dict[str, Any]:
        """
        Parses a natural language user prompt into structured parameters.
        """
        cleaned_text = prompt.strip()
        lower_text = cleaned_text.lower()

        # 1. Extract Stated Budget
        budget_info = cls._extract_budget(lower_text)

        # 2. Extract Requested Categories
        categories = cls._extract_categories(lower_text)

        # 3. Extract User Priorities
        priority_info = cls._extract_priority(lower_text)

        # 4. Extract Scenario Context
        context = cls._extract_context(lower_text)

        # 5. Extract Follow-Up Action Type (Chat dialogue classification)
        intent_type = cls._classify_intent_type(lower_text, categories, budget_info)

        # 6. Extract Mentioned Item Swaps or Specific Products
        swap_info = cls._extract_swap_request(lower_text)

        return {
            "original_prompt": cleaned_text,
            "intent_type": intent_type,
            "categories": categories,
            "category_count": len(categories),
            "stated_budget": budget_info["amount"],
            "budget_type": budget_info["type"],
            "currency": budget_info["currency"],
            "priority": priority_info["primary"],
            "priority_weights": priority_info["weights"],
            "context": context,
            "swap_request": swap_info,
            "confidence_score": cls._calculate_confidence(categories, budget_info, intent_type)
        }

    @classmethod
    def _extract_budget(cls, text: str) -> Dict[str, Any]:
        """Extracts monetary budget amount and qualifiers."""
        # Check patterns like: $150, $150.00, 150 dollars, budget of 150, max 150, under $150
        patterns = [
            r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)",                      # $150 or $150.00
            r"([0-9]+(?:\.[0-9]{1,2})?)\s*(?:dollars|usd|bucks)",   # 150 dollars
            r"budget\s*(?:of|is|:)?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)",  # budget of 150
            r"(?:under|within|max|maximum|strict|limit)\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)",  # strict 150
            r"spend\s*(?:up to|at most|no more than)?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"
        ]

        amount: Optional[float] = None
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    val = float(match.group(1))
                    if val > 0:
                        amount = val
                        break
                except ValueError:
                    continue

        # Qualifiers
        budget_type = "flexible"
        if any(word in text for word in ["strict", "hard limit", "maximum", "max", "no more than", "cap", "not exceed"]):
            budget_type = "strict"

        return {
            "amount": amount,
            "type": budget_type,
            "currency": "USD"
        }

    @classmethod
    def _extract_categories(cls, text: str) -> List[str]:
        """Identifies target product categories from user phrasing."""
        matched_categories = []
        for cat, synonyms in cls.CATEGORY_SYNONYMS.items():
            for syn in synonyms:
                # Use word boundary search where appropriate
                pattern = r"\b" + re.escape(syn) + r"\b"
                if re.search(pattern, text):
                    if cat not in matched_categories:
                        matched_categories.append(cat)
                    break
        return matched_categories

    @classmethod
    def _extract_priority(cls, text: str) -> Dict[str, Any]:
        """Determines primary optimization priority and weighted scoring."""
        scores = {
            "reliability": 0.0,
            "cost": 0.0,
            "delivery_speed": 0.0,
            "warranty": 0.0
        }

        for prio, keywords in cls.PRIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[prio] += 1.0

        # Check for explicit statements like "prioritize reliability"
        if re.search(r"prioritize\s+reliab", text) or "high reliability" in text:
            scores["reliability"] += 3.0
        if re.search(r"prioritize\s+(?:cost|cheap|savings|budget)", text) or "cheapest" in text:
            scores["cost"] += 3.0
        if re.search(r"prioritize\s+(?:speed|delivery|fast|urgent)", text):
            scores["delivery_speed"] += 3.0

        # Determine primary priority
        primary = max(scores, key=scores.get)
        if scores[primary] == 0:
            # Default to balanced reliability if none specified
            primary = "reliability"

        # Standardized weights for ranking engine (summing to 1.0)
        weight_maps = {
            "reliability": {"reliability": 0.55, "cost": 0.25, "delivery_speed": 0.10, "warranty": 0.10},
            "cost": {"reliability": 0.20, "cost": 0.65, "delivery_speed": 0.075, "warranty": 0.075},
            "delivery_speed": {"reliability": 0.30, "cost": 0.20, "delivery_speed": 0.40, "warranty": 0.10},
            "warranty": {"reliability": 0.35, "cost": 0.20, "delivery_speed": 0.10, "warranty": 0.35}
        }

        return {
            "primary": primary,
            "weights": weight_maps.get(primary, weight_maps["reliability"])
        }

    @classmethod
    def _extract_context(cls, text: str) -> str:
        """Extracts contextual background situation."""
        for ctx, keywords in cls.CONTEXT_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    return ctx
        return "general_shopping"

    @classmethod
    def _classify_intent_type(
        cls,
        text: str,
        categories: List[str],
        budget_info: Dict[str, Any]
    ) -> str:
        """Classifies the primary operational intent of the prompt."""
        # 1. Emergency optimization (e.g., "broken laptop", "urgent replacement", "emergency")
        if any(w in text for w in ["emergency", "urgent", "broken", "died", "cracked"]) and categories:
            return "EMERGENCY_OPTIMIZATION"

        # 2. Trade-off question (e.g., "Why did you pick TaoTronics?", "Why not BenQ?")
        if any(w in text for w in ["why did you", "why not", "why choose", "explain trade-off", "explain why", "trade-offs"]):
            return "TRADE_OFF_QUERY"

        # 3. Budget adjustment (e.g., "What if my budget is $120?", "I only have $100")
        if any(w in text for w in ["what if", "change budget", "new budget", "reduce budget", "increase budget"]) and budget_info["amount"]:
            return "BUDGET_ADJUSTMENT"

        # 4. Checkout / payment intent (e.g., "Proceed to checkout", "Buy now", "Pay with paypal")
        if any(w in text for w in ["checkout", "pay now", "proceed to pay", "paypal checkout", "complete purchase", "buy this"]):
            return "CHECKOUT_INTENT"

        # 5. Swap / customization request in dialogue (e.g., "Swap lamp for cheaper", "Switch earbuds to Sony")
        if re.search(r"\b(?:swap|switch|change\s+the)\b", text):
            return "SWAP_REQUEST"

        # 6. Multi-Item bundle optimization
        if len(categories) > 1 or (len(categories) == 1 and budget_info["amount"]):
            return "MULTI_ITEM_OPTIMIZATION"

        return "GENERAL_INQUIRY"

    @classmethod
    def _extract_swap_request(cls, text: str) -> Optional[Dict[str, str]]:
        """Extracts specific item swap targets if present."""
        match = re.search(r"swap\s+([a-zA-Z0-9_\-\s]+)\s+(?:for|with|to)\s+([a-zA-Z0-9_\-\s]+)", text)
        if match:
            return {
                "replace_target": match.group(1).strip(),
                "replacement_candidate": match.group(2).strip()
            }
        return None

    @classmethod
    def _calculate_confidence(
        cls,
        categories: List[str],
        budget_info: Dict[str, Any],
        intent_type: str
    ) -> float:
        """Computes confidence score of intent parsing."""
        score = 0.5
        if categories:
            score += min(len(categories) * 0.15, 0.3)
        if budget_info["amount"] is not None:
            score += 0.15
        if intent_type != "GENERAL_INQUIRY":
            score += 0.05
        return round(min(score, 1.0), 2)

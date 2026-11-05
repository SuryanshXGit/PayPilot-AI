"""
PayPilot AI - AI & Chatbot REST API Routes
Module Owner: Shubhneet

Exposes REST endpoints for:
- AI Intent Parsing (/api/ai/parse-intent)
- Multi-Item Bundle Optimization & Ranking (/api/ai/recommend-bundle)
- Multi-Turn Conversational Assistant (/api/ai/chat)
- Deep Trade-Off Explanations (/api/ai/explain-tradeoffs)
- Voice Command Processing with Payment Guardrails (/api/ai/voice-command)
- Zero-Spam Financial Smart Filter (/api/ai/smart-filter)
- Pre-configured Demo Scenarios (/api/ai/scenarios)
"""

from app.services.gemini_service import GeminiService
from flask import Blueprint, request, jsonify
from app.services.ai_intent_parser import AIIntentParser
from app.services.ai_ranking_engine import AIRankingEngine
from app.services.ai_tradeoff_explainer import AITradeOffExplainer
from app.services.ai_conversational_assistant import AIConversationalAssistant
from app.services.voice_command_service import VoiceCommandService
from app.services.financial_smart_filter import FinancialSmartFilter
from app.services.catalogue_service import CatalogueService
from app.services.budget_guard import BudgetGuardService

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# Singleton conversational assistant instance
chat_assistant = AIConversationalAssistant()


@ai_bp.route("/parse-intent", methods=["POST"])
def parse_intent():
    """
    Parses natural language prompt into structured categories, budget,
    priority weights, and context.
    """
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"status": "error", "message": "Missing 'prompt' in request body"}), 400

    parsed = AIIntentParser.parse(prompt)
    return jsonify({
        "status": "success",
        "result": parsed
    })


@ai_bp.route("/recommend-bundle", methods=["POST"])
def recommend_bundle():
    """
    Core Multi-Item Budget Optimization & Ranking endpoint.
    Evaluates product options across categories, balances constraints,
    and returns ranked bundles with deterministic trade-off explanations.
    """
    data = request.get_json(silent=True) or {}
    categories = data.get("categories", ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"])
    stated_budget = data.get("stated_budget", 150.0)
    priority = data.get("priority", "reliability")
    apply_tax = data.get("apply_tax", False)
    apply_shipping = data.get("apply_shipping", False)

    try:
        stated_budget = float(stated_budget)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid stated_budget value"}), 400

    # Execute multi-constraint ranking
    opt_result = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=stated_budget,
        priority=priority,
        apply_tax=apply_tax,
        apply_shipping=apply_shipping
    )

    if opt_result.get("error"):
        return jsonify({"status": "error", "message": opt_result["error"]}), 404

    # Generate rich trade-off explanations
    explanations = AITradeOffExplainer.explain_bundle_recommendation(
        recommended_bundle=opt_result["recommended_bundle"],
        budget_saver_bundle=opt_result["budget_saver_bundle"],
        premium_bundle=opt_result["premium_bundle"],
        stated_budget=stated_budget,
        priority=priority,
        category_products=opt_result["category_products"]
    )

    # Format items to dicts
    def bundle_to_dict(bundle):
        if not bundle:
            return None
        return {
            "total_cost": bundle["total_cost"],
            "subtotal": bundle["subtotal"],
            "is_within_budget": bundle["is_within_budget"],
            "surplus": bundle["surplus"],
            "shortfall": bundle["shortfall"],
            "average_reliability": bundle["average_reliability"],
            "max_delivery_days": bundle.get("max_delivery_days"),
            "average_warranty_months": bundle.get("average_warranty_months"),
            "items": [it.to_dict() if hasattr(it, "to_dict") else it for it in bundle["items"]]
        }

    return jsonify({
        "status": "success",
        "stated_budget": stated_budget,
        "priority": priority,
        "total_combinations_evaluated": opt_result["total_combinations_evaluated"],
        "feasible_combinations_count": opt_result["feasible_combinations_count"],
        "recommended_bundle": bundle_to_dict(opt_result["recommended_bundle"]),
        "budget_saver_bundle": bundle_to_dict(opt_result["budget_saver_bundle"]),
        "premium_bundle": bundle_to_dict(opt_result["premium_bundle"]),
        "fast_bundle": bundle_to_dict(opt_result.get("fast_bundle")),
        "trade_off_explanations": explanations,
        "guardrail_verification": {
            "calculation_basis": "deterministic_catalogue_lookup",
            "hallucination_risk": "0%",
            "source_label": "Controlled Catalogue Price (Verified Retail Benchmark)"
        }
    })


@ai_bp.route("/chat", methods=["POST"])
def chat():
    """
    Multi-Turn AI Shopping Assistant endpoint.
    Maintains dialogue session state, interprets adjustments and queries,
    and returns conversational text with Budget Guard status.
    """
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id", "default_session")
    message = data.get("message", "")
    override_budget = data.get("stated_budget")
    override_priority = data.get("priority")

    if not message:
        return jsonify({"status": "error", "message": "Missing 'message' in request body"}), 400

    chat_resp = chat_assistant.process_message(
        session_id=session_id,
        user_message=message,
        override_budget=override_budget,
        override_priority=override_priority
    )

    # Convert bundle items to serializable dicts if present
    bundle_data = None
    if chat_resp.get("bundle"):
        b = chat_resp["bundle"]
        bundle_data = {
            "total_cost": b["total_cost"],
            "subtotal": b["subtotal"],
            "is_within_budget": b["is_within_budget"],
            "surplus": b.get("surplus", 0.0),
            "shortfall": b.get("shortfall", 0.0),
            "average_reliability": b.get("average_reliability", 0.0),
            "items": [it.to_dict() if hasattr(it, "to_dict") else it for it in b["items"]]
        }
    # Enhance the existing response using Gemini
    try:
        gemini_reply = GeminiService.generate_reply(
            user_message=message,
            deterministic_reply=chat_resp["reply_text"],
            bundle=bundle_data
        )

        if gemini_reply:
            chat_resp["reply_text"] = gemini_reply

    except Exception as error:
        print(f"Gemini enhancement unavailable: {error}")
    return jsonify({
        "status": "success",
        "session_id": session_id,
        "reply_text": chat_resp["reply_text"],
        "intent": chat_resp.get("intent"),
        "bundle": bundle_data,
        "explanations": chat_resp.get("explanations", []),
        "suggested_actions": chat_resp.get("suggested_actions", [])
    })


@ai_bp.route("/explain-tradeoffs", methods=["POST"])
def explain_tradeoffs():
    """
    Provides comprehensive trade-off analysis comparing two bundles or
    explaining an individual bundle.
    """
    data = request.get_json(silent=True) or {}
    item_ids = data.get("item_ids", [])
    stated_budget = float(data.get("stated_budget", 150.0))
    priority = data.get("priority", "reliability")

    products = CatalogueService.get_products_by_ids(item_ids)
    if not products:
        return jsonify({"status": "error", "message": "No valid products found for item_ids"}), 404

    totals = BudgetGuardService.calculate_totals(products)
    avg_rel = round(sum(p.reliability_score for p in products) / len(products), 2)

    categories = list({p.category for p in products})
    opt_result = AIRankingEngine.optimize_multi_item_bundle(
        categories=categories,
        stated_budget=stated_budget,
        priority=priority
    )

    explanations = AITradeOffExplainer.explain_bundle_recommendation(
        recommended_bundle=opt_result["recommended_bundle"],
        budget_saver_bundle=opt_result["budget_saver_bundle"],
        premium_bundle=opt_result["premium_bundle"],
        stated_budget=stated_budget,
        priority=priority,
        category_products=opt_result["category_products"]
    )

    return jsonify({
        "status": "success",
        "stated_budget": stated_budget,
        "total_cost": totals["total"],
        "average_reliability": avg_rel,
        "is_within_budget": totals["total"] <= stated_budget,
        "explanations": explanations
    })


@ai_bp.route("/voice-command", methods=["POST"])
def voice_command():
    """
    Interprets transcribed speech commands with safety checks.
    Enforces mandatory explicit confirmation before any payment-related action.
    """
    data = request.get_json(silent=True) or {}
    transcript = data.get("transcript", "")
    bundle_total = data.get("current_bundle_total")
    item_count = int(data.get("item_count", 3))

    if not transcript:
        return jsonify({"status": "error", "message": "Missing 'transcript' in request body"}), 400

    result = VoiceCommandService.process_voice_transcript(
        transcript=transcript,
        current_bundle_total=bundle_total,
        item_count=item_count
    )

    return jsonify({
        "status": "success",
        "result": result
    })


@ai_bp.route("/smart-filter", methods=["POST"])
def smart_filter():
    """
    Zero-Spam Financial Smart Filter endpoint.
    Classifies messages into IMPORTANT, PROMOTIONAL, SUSPICIOUS, NEEDS_REVIEW
    and explains warning signs without silently deleting.
    """
    data = request.get_json(silent=True) or {}
    sender = data.get("sender", "")
    subject = data.get("subject", "")
    body = data.get("body", "")

    if not body:
        return jsonify({"status": "error", "message": "Missing message 'body' in request body"}), 400

    classification = FinancialSmartFilter.classify_message(
        sender=sender,
        subject=subject,
        body=body
    )

    return jsonify({
        "status": "success",
        "result": classification
    })


@ai_bp.route("/smart-filter/samples", methods=["GET"])
def smart_filter_samples():
    """Returns sample messages for demonstration."""
    return jsonify({
        "status": "success",
        "samples": FinancialSmartFilter.SAMPLE_MESSAGES
    })


@ai_bp.route("/scenarios", methods=["GET"])
def get_scenarios():
    """Returns pre-configured demo scenarios."""
    scenarios = [
        {
            "id": "dorm_scenario",
            "name": "College Dorm Move-In (Jaw-Dropping Demo)",
            "prompt": "I'm a college student moving into an unfurnished dorm with a strict $150 total budget. I need a desk lamp, a portable steamer, and noise-cancelling study buds. Prioritize reliability and explain compromises.",
            "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
            "stated_budget": 150.0,
            "priority": "reliability",
            "expected_total": 137.97,
            "expected_surplus": 12.03
        },
        {
            "id": "emergency_laptop",
            "name": "Emergency Broken Laptop Replacement",
            "prompt": "My work laptop broke and I need an urgent replacement under $500 with guaranteed 1-day delivery and strong warranty. Prioritize delivery turnaround.",
            "categories": ["laptop"],
            "stated_budget": 500.0,
            "priority": "delivery_speed",
            "expected_recommendation": "Lenovo ThinkPad T14s Refurbished ($499.00, 1-day delivery)"
        },
        {
            "id": "emergency_medical",
            "name": "Emergency Medical Expense Navigator",
            "prompt": "Unexpected medical need for home diagnostic health equipment under $200. Prioritize highest reliability score.",
            "categories": ["medical_equipment"],
            "stated_budget": 200.0,
            "priority": "reliability"
        }
    ]
    return jsonify({
        "status": "success",
        "scenarios": scenarios
    })

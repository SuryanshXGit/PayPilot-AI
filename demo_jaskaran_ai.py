"""
=============================================================================
PayPilot AI 2.0 — End-to-End AI Assistant & Reasoning Demonstration
Module Owner: Jaskaran (AI Intent Parsing, Product Ranking, Chatbot, Voice, Smart Filter)
=============================================================================

Executes a live walkthrough of:
1. The Jaw-Dropping Demo: College Dorm Move-In ($150 Strict Budget, 3 Items)
2. Conversational Follow-Up: Trade-Off Questions & Dynamic Budget Reduction ($120)
3. Emergency Expense Navigator: Broken Work Laptop Replacement ($500 Budget)
4. Hands-Free Voice Command Processor with Strict Payment Confirmation Guardrail
5. Zero-Spam Financial Smart Filter: Phishing Detection & Red Flag Analysis
"""

import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from app import create_app
from app.services.ai_intent_parser import AIIntentParser
from app.services.ai_ranking_engine import AIRankingEngine
from app.services.ai_tradeoff_explainer import AITradeOffExplainer
from app.services.ai_conversational_assistant import AIConversationalAssistant
from app.services.voice_command_service import VoiceCommandService
from app.services.financial_smart_filter import FinancialSmartFilter


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def print_step(title: str):
    print(f"\n---> {title}")


def run_demo():
    app = create_app()

    with app.app_context():
        # =====================================================================
        # SCENARIO 1: THE JAW-DROPPING DEMO (COLLEGE DORM MOVE-IN)
        # =====================================================================
        print_header("Scenario 1: College Student Dorm Move-In ($150 Strict Budget)")

        prompt_1 = (
            "I'm a college student moving into an unfurnished dorm with a strict $150 total budget. "
            "I need a desk lamp, a portable steamer, and noise-cancelling study buds. "
            "Prioritize reliability and explain compromises."
        )
        print(f"User Utterance: \"{prompt_1}\"\n")

        print_step("Step 1.1: AI Natural Language Intent Parsing")
        parsed_1 = AIIntentParser.parse(prompt_1)
        print(f"  • Extracted Categories : {parsed_1['categories']}")
        print(f"  • Stated Budget        : ${parsed_1['stated_budget']:.2f} ({parsed_1['budget_type']})")
        print(f"  • Primary Priority     : {parsed_1['priority'].upper()}")
        print(f"  • Scenario Context     : {parsed_1['context']}")
        print(f"  • Confidence Score     : {parsed_1['confidence_score'] * 100:.0f}%")

        print_step("Step 1.2: Multi-Constraint Product Ranking & Optimization")
        opt_1 = AIRankingEngine.optimize_multi_item_bundle(
            categories=parsed_1["categories"],
            stated_budget=parsed_1["stated_budget"],
            priority=parsed_1["priority"]
        )
        rec = opt_1["recommended_bundle"]
        saver = opt_1["budget_saver_bundle"]
        prem = opt_1["premium_bundle"]

        print(f"  • Total Combinations Evaluated in Search Space: {opt_1['total_combinations_evaluated']}")
        print(f"  • Feasible Combinations Under $150 Cap         : {opt_1['feasible_combinations_count']}")
        print("\n  ★ AI Recommended Optimal Bundle:")
        for it in rec["items"]:
            print(f"    - {it.name:<50} | ${it.price:>6.2f} | ★ {it.reliability_score}/10")
        print(f"    ----------------------------------------------------------------------")
        print(f"    Deterministic Bundle Total: ${rec['total_cost']:.2f} USD")
        print(f"    Budget Guard Surplus Buffer: +${rec['surplus']:.2f} remaining under ${parsed_1['stated_budget']:.2f}")
        print(f"    Average Reliability Score  : {rec['average_reliability']}/10")

        print_step("Step 1.3: Deep AI Trade-Off & Compromise Explanations")
        explanations = AITradeOffExplainer.explain_bundle_recommendation(
            recommended_bundle=rec,
            budget_saver_bundle=saver,
            premium_bundle=prem,
            stated_budget=parsed_1["stated_budget"],
            priority=parsed_1["priority"],
            category_products=opt_1["category_products"]
        )
        for idx, exp in enumerate(explanations, 1):
            print(f"  [{idx}] {exp}")

        # =====================================================================
        # SCENARIO 2: CONVERSATIONAL FOLLOW-UP & DYNAMIC BUDGET ADJUSTMENT
        # =====================================================================
        print_header("Scenario 2: Multi-Turn Conversational Dialogue (Idea 05)")
        bot = AIConversationalAssistant()
        session_id = "demo_walkthrough_session"

        # Turn 1: Initial Prompt
        bot.process_message(session_id, prompt_1)

        # Turn 2: User asks why BenQ lamp was not selected
        q2 = "Why did you pick TaoTronics desk lamp instead of BenQ?"
        print(f"\nUser Query: \"{q2}\"")
        resp_turn2 = bot.process_message(session_id, q2)
        print("\nPayPilot AI Conversational Response:")
        print(resp_turn2["reply_text"])

        # Turn 3: User reduces budget to $120
        q3 = "What if my budget is only $120?"
        print(f"\nUser Adjustment: \"{q3}\"")
        resp_turn3 = bot.process_message(session_id, q3)
        print("\nPayPilot AI Dynamic Re-Optimization:")
        print(resp_turn3["reply_text"])
        b3 = resp_turn3["bundle"]
        print(f"  --> Updated Bundle Total: ${b3['total_cost']:.2f} (Under $120.00 Budget Guard!)")

        # =====================================================================
        # SCENARIO 3: EMERGENCY EXPENSE NAVIGATOR (IDEA 08)
        # =====================================================================
        print_header("Scenario 3: Emergency Expense Navigator (Broken Work Laptop)")
        emergency_prompt = "My work laptop broke and I need an urgent replacement under $500 with guaranteed 1-day delivery and strong warranty."
        print(f"User Utterance: \"{emergency_prompt}\"\n")

        parsed_em = AIIntentParser.parse(emergency_prompt)
        opt_em = AIRankingEngine.optimize_multi_item_bundle(
            categories=["laptop"],
            stated_budget=500.0,
            priority="delivery_speed"
        )
        rec_em = opt_em["recommended_bundle"]
        selected_laptop = rec_em["items"][0]

        print(f"  • Selected Item     : {selected_laptop.name}")
        print(f"  • Price & Budget    : ${selected_laptop.price:.2f} (Within $500.00 Limit)")
        print(f"  • Delivery Speed    : {selected_laptop.delivery_days} Day Turnaround")
        print(f"  • Warranty Coverage : {selected_laptop.warranty_months} Months")
        print(f"  • Reliability Score : ★ {selected_laptop.reliability_score}/10")

        # =====================================================================
        # SCENARIO 4: HANDS-FREE VOICE COMMANDS WITH PAYMENT GUARDRAIL (IDEA 02)
        # =====================================================================
        print_header("Scenario 4: Hands-Free Voice Commands & Safety Checklist (Idea 02)")

        # Command A: Safe navigation voice input
        voice_a = "Optimize college dorm move in"
        print(f"Spoken Input A: \"{voice_a}\"")
        res_va = VoiceCommandService.process_voice_transcript(voice_a, current_bundle_total=137.97)
        print(f"  • Interpreted Action       : {res_va['interpreted_action']}")
        print(f"  • Requires Confirmation    : {res_va['requires_explicit_confirmation']}")
        print(f"  • TTS Feedback             : \"{res_va['tts_speech_response']}\"")

        # Command B: Payment command triggering guardrail
        voice_b = "Checkout and pay with PayPal Sandbox now"
        print(f"\nSpoken Input B: \"{voice_b}\"")
        res_vb = VoiceCommandService.process_voice_transcript(voice_b, current_bundle_total=137.97, item_count=3)
        print(f"  • Interpreted Action       : {res_vb['interpreted_action']}")
        print(f"  • Requires Confirmation    : {res_vb['requires_explicit_confirmation']} (MANDATORY GUARDRAIL)")
        print(f"  • Security Prompt          : \"{res_vb['confirmation_prompt']}\"")
        print(f"  • Checklist Rule           : {res_vb['safety_checklist_rule']}")

        # =====================================================================
        # SCENARIO 5: ZERO-SPAM FINANCIAL SMART FILTER (IDEA 07)
        # =====================================================================
        print_header("Scenario 5: Zero-Spam Financial Smart Filter (Idea 07)")

        # Test Phishing Message
        phish = {
            "sender": "+1 (800) 555-0199",
            "subject": "PAYPAL URGENT: Account Suspended",
            "body": "URGENT: Your PayPal account has been suspended due to unauthorized activity. Verify your PIN and identity within 24 hours at http://paypa1-security-verification.xyz/login to restore access."
        }
        res_filter = FinancialSmartFilter.classify_message(**phish)
        print(f"Inspecting Message: \"{phish['subject']}\" from {phish['sender']}")
        print(f"  • Classification Category  : {res_filter['category']}")
        print(f"  • Assessed Risk Level      : {res_filter['risk_level']}")
        print(f"  • Warning Signs Identified :")
        for sign in res_filter['warning_signs']:
            print(f"    ⚠️  {sign}")
        print(f"  • Action Recommendation    : {res_filter['action_recommendation']}")
        print(f"  • Silently Deleted?        : {res_filter['silently_deleted']} (Guardrail: Never silently deleted!)")
        print(f"  • Disclaimer               : {res_filter['guardrail_disclaimer']}")

        print("\n" + "=" * 80)
        print("  JASKARAN AI DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=============================================================================\n")


if __name__ == "__main__":
    run_demo()

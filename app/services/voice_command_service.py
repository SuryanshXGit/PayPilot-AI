"""
PayPilot AI - Hands-Free Voice Command Processor (Idea 02)
Module Owner: Shubhneet

Processes natural speech / transcribed voice input:
- Maps natural spoken phrases to application actions (bundle optimization, navigation, swaps)
- Formats synthesized speech-friendly text outputs for TTS engines
- STRICT GUARDRAIL ENFORCEMENT: Enforces mandatory explicit confirmation before any
  payment-related action. Voice triggers will never execute payment without verified user consent.
"""

import re
from typing import Dict, Any, Optional
from app.services.ai_intent_parser import AIIntentParser


class VoiceCommandService:
    """
    Interprets speech input into structured system actions with safety guardrails.
    """

    # Spoken command regex patterns
    COMMAND_PATTERNS = {
        "OPTIMIZE_DORM": [
            r"dorm\s+move\s*in", r"college\s+dorm", r"dorm\s+bundle",
            r"optimize\s+dorm", r"student\s+bundle", r"dorm\s+set"
        ],
        "EMERGENCY_LAPTOP": [
            r"emergency\s+laptop", r"broken\s+laptop", r"laptop\s+broke",
            r"urgent\s+laptop", r"replacement\s+laptop"
        ],
        "CHECK_BUDGET": [
            r"check\s+(?:my\s+)?budget", r"recalculate", r"how\s+much\s+left",
            r"am\s+i\s+over\s+budget", r"budget\s+check", r"what\s+is\s+my\s+total"
        ],
        "SWAP_CHEAPER": [
            r"make\s+it\s+cheaper", r"show\s+cheaper", r"cheaper\s+options",
            r"budget\s+saver", r"lowest\s+cost"
        ],
        "READ_SUMMARY": [
            r"read\s+summary", r"read\s+aloud", r"speak\s+summary",
            r"tell\s+me\s+the\s+trade-?offs", r"read\s+trade-?offs"
        ],
        "TOGGLE_HIGH_CONTRAST": [
            r"toggle\s+high\s+contrast", r"high\s+contrast\s+mode",
            r"switch\s+to\s+high\s+contrast", r"turn\s+on\s+high\s+contrast"
        ],
        "INCREASE_TEXT": [
            r"increase\s+text\s+size", r"make\s+text\s+larger",
            r"bigger\s+text", r"large\s+font"
        ],
        "INITIATE_PAYMENT": [
            r"checkout", r"pay\s+now", r"proceed\s+to\s+payment",
            r"pay\s+with\s+paypal", r"complete\s+purchase", r"buy\s+these\s+items",
            r"authorize\s+payment"
        ],
        "CONFIRM_YES": [
            r"yes\s+confirm", r"i\s+confirm", r"confirm\s+payment",
            r"yes\s+proceed", r"yes\s+i\s+approve", r"approved"
        ],
        "CONFIRM_NO": [
            r"cancel\s+payment", r"no\s+cancel", r"do\s+not\s+pay",
            r"stop", r"abort"
        ]
    }

    @classmethod
    def process_voice_transcript(
        cls,
        transcript: str,
        current_bundle_total: Optional[float] = None,
        item_count: int = 3
    ) -> Dict[str, Any]:
        """
        Parses transcribed speech, identifies action, and applies safety checks.
        """
        cleaned = transcript.strip()
        lower = cleaned.lower()

        detected_action = "GENERAL_SHOPPING_PROMPT"
        requires_confirmation = False
        is_payment_action = False
        confirmation_prompt = None

        # Check action pattern matches
        for action, patterns in cls.COMMAND_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, lower):
                    detected_action = action
                    break
            if detected_action != "GENERAL_SHOPPING_PROMPT":
                break

        # Safety Checklist Guardrail:
        # Require explicit confirmation before payment-related actions
        total_disp = f"${current_bundle_total:.2f}" if current_bundle_total else "the current order amount"

        if detected_action == "INITIATE_PAYMENT":
            requires_confirmation = True
            is_payment_action = True
            confirmation_prompt = (
                f"Security Guardrail: Voice commands require explicit verification before payment. "
                f"Do you authorize initiating PayPal Sandbox checkout for {total_disp} ({item_count} items)?"
            )
            tts_speech = (
                f"Payment confirmation required. Please confirm if you wish to proceed to PayPal Sandbox "
                f"checkout for {total_disp}."
            )
        elif detected_action == "CONFIRM_YES":
            tts_speech = "Payment authorization confirmed by user. Proceeding to PayPal Sandbox checkout."
        elif detected_action == "CONFIRM_NO":
            tts_speech = "Payment cancelled. Returning to shopping review."
        elif detected_action == "OPTIMIZE_DORM":
            tts_speech = "Optimizing college dorm move-in basket for lamp, steamer, and study buds under $150 budget."
        elif detected_action == "EMERGENCY_LAPTOP":
            tts_speech = "Loading emergency laptop replacement options focusing on 1-day turnaround and warranty."
        elif detected_action == "CHECK_BUDGET":
            tts_speech = f"Calculating deterministic totals with Budget Guard. Order amount is {total_disp}."
        elif detected_action == "SWAP_CHEAPER":
            tts_speech = "Switching to Budget Saver configuration to minimize your out-of-pocket costs."
        elif detected_action == "READ_SUMMARY":
            tts_speech = "Reading aloud trade-off explanations and verified bundle totals."
        elif detected_action == "TOGGLE_HIGH_CONTRAST":
            tts_speech = "Toggling high-contrast universal accessibility mode."
        elif detected_action == "INCREASE_TEXT":
            tts_speech = "Adjusting typographic scale for improved visual comfort."
        else:
            # Fall back to general NLP intent parsing
            parsed = AIIntentParser.parse(cleaned)
            tts_speech = f"Interpreted shopping request for {len(parsed['categories'])} items within stated budget."

        return {
            "status": "success",
            "raw_transcript": cleaned,
            "interpreted_action": detected_action,
            "requires_explicit_confirmation": requires_confirmation,
            "is_payment_action": is_payment_action,
            "confirmation_prompt": confirmation_prompt,
            "tts_speech_response": tts_speech,
            "safety_checklist_rule": "Voice commands require explicit user confirmation before any payment action."
        }

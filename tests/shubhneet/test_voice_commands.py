"""
Unit tests for VoiceCommandService (Idea 02)
Module Owner: Shubhneet
"""

import pytest
from app.services.voice_command_service import VoiceCommandService


def test_voice_dorm_command():
    resp = VoiceCommandService.process_voice_transcript(
        transcript="Optimize college dorm move in for lamp steamer and buds under 150 dollars",
        current_bundle_total=137.97
    )

    assert resp["interpreted_action"] == "OPTIMIZE_DORM"
    assert resp["requires_explicit_confirmation"] is False
    assert resp["is_payment_action"] is False


def test_voice_payment_guardrail_enforcement():
    """
    CRITICAL CHECKLIST TEST:
    Voice input for payment actions MUST require explicit confirmation!
    """
    resp = VoiceCommandService.process_voice_transcript(
        transcript="Checkout and pay with PayPal now",
        current_bundle_total=137.97,
        item_count=3
    )

    assert resp["interpreted_action"] == "INITIATE_PAYMENT"
    assert resp["requires_explicit_confirmation"] is True
    assert resp["is_payment_action"] is True
    assert "$137.97" in resp["confirmation_prompt"]
    assert "explicit" in resp["confirmation_prompt"].lower() or "verification" in resp["confirmation_prompt"].lower()


def test_voice_payment_confirmation_affirmative():
    resp = VoiceCommandService.process_voice_transcript(
        transcript="Yes confirm payment",
        current_bundle_total=137.97
    )

    assert resp["interpreted_action"] == "CONFIRM_YES"
    assert resp["requires_explicit_confirmation"] is False
    assert "confirmed" in resp["tts_speech_response"].lower()


def test_voice_payment_cancellation():
    resp = VoiceCommandService.process_voice_transcript(
        transcript="Cancel payment",
        current_bundle_total=137.97
    )

    assert resp["interpreted_action"] == "CONFIRM_NO"
    assert resp["requires_explicit_confirmation"] is False
    assert "cancelled" in resp["tts_speech_response"].lower()

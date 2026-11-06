"""
Unit tests for FinancialSmartFilter (Idea 07)
Module Owner: Jaskaran
"""

import pytest
from app.services.financial_smart_filter import FinancialSmartFilter


def test_classify_phishing_message():
    sample = {
        "sender": "+1 (800) 555-0199",
        "subject": "PAYPAL URGENT: Account Suspended",
        "body": "URGENT: Your PayPal account has been suspended due to unauthorized activity. Verify your PIN and identity within 24 hours at http://paypa1-security-verification.xyz/login to restore access."
    }
    result = FinancialSmartFilter.classify_message(**sample)

    assert result["category"] == "SUSPICIOUS"
    assert result["risk_level"] == "HIGH"
    assert len(result["warning_signs"]) >= 2
    assert result["silently_deleted"] is False
    assert "guidance" in result["guardrail_disclaimer"].lower() or "heuristic" in result["guardrail_disclaimer"].lower()


def test_classify_promotional_email():
    sample = {
        "sender": "offers@e.shoppingdeals.com",
        "subject": "Exclusive 30% Off Back-to-School Dorm Essentials!",
        "body": "Huge Flash Sale! Use promo code DORM30 to get 30% off desk lamps and steamers. Limited time offer!"
    }
    result = FinancialSmartFilter.classify_message(**sample)

    assert result["category"] == "PROMOTIONAL"
    assert result["risk_level"] == "LOW"
    assert result["silently_deleted"] is False


def test_classify_authentic_receipt():
    sample = {
        "sender": "service@paypal.com",
        "subject": "Receipt for your payment of $137.97 to PayPilot Demo Store",
        "body": "Hello College Student, you sent a payment of $137.97 USD to PayPilot Demo Store. Payment Confirmation ID: 9BT48291KL382."
    }
    result = FinancialSmartFilter.classify_message(**sample)

    assert result["category"] == "IMPORTANT"
    assert result["risk_level"] == "LOW"
    assert result["silently_deleted"] is False


def test_guardrail_no_silent_delete_or_definitive_claim():
    """
    CHECKLIST TEST:
    Must never claim 100% definitive fraud detection and never silently delete.
    """
    sample = {
        "sender": "random@unknown.com",
        "subject": "Unknown delivery notice",
        "body": "Your parcel is pending an unpaid fee."
    }
    result = FinancialSmartFilter.classify_message(**sample)

    assert result["silently_deleted"] is False
    assert "heuristic" in result["guardrail_disclaimer"].lower()

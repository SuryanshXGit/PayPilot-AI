"""
Unit tests for AIConversationalAssistant
Module Owner: Shubhneet
"""

import pytest
from app.services.ai_conversational_assistant import AIConversationalAssistant


@pytest.fixture
def chat_bot(app_context):
    return AIConversationalAssistant()


def test_initial_dorm_prompt(chat_bot):
    resp = chat_bot.process_message(
        session_id="test_session_1",
        user_message="I'm a college student moving into a dorm with strict $150 budget. Need lamp, steamer, earbuds. Prioritize reliability."
    )

    assert resp["bundle"] is not None
    assert resp["bundle"]["total_cost"] == 137.97
    assert resp["bundle"]["is_within_budget"] is True
    assert "137.97" in resp["reply_text"]
    assert len(resp["explanations"]) > 0


def test_follow_up_tradeoff_query(chat_bot):
    chat_bot.process_message(
        session_id="test_session_2",
        user_message="Optimize dorm move in under $150."
    )
    # Ask why BenQ wasn't chosen
    resp = chat_bot.process_message(
        session_id="test_session_2",
        user_message="Why didn't you pick the BenQ lamp?"
    )

    assert resp["intent"] == "TRADE_OFF_QUERY"
    assert "benq" in resp["reply_text"].lower()
    assert "56.01" in resp["reply_text"] or "saving" in resp["reply_text"].lower()


def test_follow_up_budget_reduction(chat_bot):
    chat_bot.process_message(
        session_id="test_session_3",
        user_message="Optimize dorm move in under $150."
    )
    # User reduces budget to $120
    resp = chat_bot.process_message(
        session_id="test_session_3",
        user_message="What if my budget is only $120?"
    )

    assert resp["bundle"] is not None
    assert resp["bundle"]["total_cost"] <= 120.0
    assert resp["bundle"]["is_within_budget"] is True


def test_pay_in_4_compliance_disclosure(chat_bot):
    resp = chat_bot.process_message(
        session_id="test_session_4",
        user_message="Can I pay using PayPal Pay in 4 installments?"
    )

    reply = resp["reply_text"].lower()
    # Must adhere to Hackathon checklist disclosures:
    assert "eligibility" in reply or "eligible" in reply
    assert "not guarantee" in reply or "not guaranteed" in reply
    assert "obligation" in reply or "total financial liability" in reply

"""
PayPilot AI - Zero-Spam Financial Smart Filter (Idea 07)
Module Owner: Shubhneet

Classifies sample / user-submitted financial messages (SMS, push, emails):
- Categories: IMPORTANT, PROMOTIONAL, SUSPICIOUS, NEEDS_REVIEW
- Analyzes warning signs: artificial urgency, spoofed domains, unexpected attachments, OTP requests
- STRICT HACKATHON GUARDRAIL ADHERENCE:
  * NEVER silently deletes messages.
  * NEVER claims definitive 100% fraud detection.
  * Discloses heuristic reasoning and warning indicators transparently.
"""

import re
from typing import Dict, Any, List


class FinancialSmartFilter:
    """
    Intelligent message classification engine for financial communications.
    """

    # Suspicious domain and phishing patterns
    SUSPICIOUS_DOMAIN_PATTERNS = [
        r"paypa[l1]-?(?:security|verify|account|update|support)",
        r"(?:bit\.ly|tinyurl\.com|t\.co|rb\.gy)\/[a-zA-Z0-9]+",
        r"secure-?(?:paypal|bank|login|auth)\.(?:xyz|top|cc|tk|ml|ga|work)",
        r"\b(?:login|signin)-paypal\.",
        r"\.ru\b|\.cn\b|\.top\b|\.xyz\b"
    ]

    # Artificial urgency phrases
    URGENCY_PATTERNS = [
        r"account\s+(?:suspended|restricted|blocked|frozen)",
        r"within\s+(?:24|12|48)\s+hours",
        r"immediate\s+action\s+required",
        r"act\s+now\s+or",
        r"permanent\s+deactivation",
        r"unauthorized\s+transaction\s+detected"
    ]

    # Sensitive data harvesting phrases
    CREDENTIAL_HARVEST_PATTERNS = [
        r"enter\s+your\s+(?:pin|password|ssn|otp|card\s+number)",
        r"confirm\s+your\s+identity\s+by\s+replying",
        r"share\s+(?:one[- ]time|secret|verification)\s+code"
    ]

    # Promotional keywords
    PROMOTIONAL_PATTERNS = [
        r"discount", r"coupon", r"promo\s*code", r"% off",
        r"limited\s+time\s+offer", r"exclusive\s+deal", r"flash\s+sale",
        r"earn\s+cashback", r"shop\s+now\s+and\s+save"
    ]

    # Important/Authentic transaction patterns
    IMPORTANT_PATTERNS = [
        r"receipt\s+for\s+your\s+payment",
        r"you\s+sent\s+\$[0-9]+(?:\.[0-9]{2})?\s+to",
        r"your\s+order\s+#[a-zA-Z0-9\-]+\s+has\s+shipped",
        r"statement\s+is\s+now\s+available",
        r"payment\s+confirmation\s+id"
    ]

    # Sample messages for interactive testing / demo
    SAMPLE_MESSAGES = [
        {
            "id": "sample-phishing-01",
            "title": "Suspicious Phishing SMS (Fake PayPal Urgency)",
            "sender": "+1 (800) 555-0199",
            "subject": "PAYPAL URGENT: Account Suspended",
            "body": "URGENT: Your PayPal account has been suspended due to unauthorized activity. Verify your PIN and identity within 24 hours at http://paypa1-security-verification.xyz/login to restore access."
        },
        {
            "id": "sample-promo-01",
            "title": "Promotional Marketing Email",
            "sender": "offers@e.shoppingdeals.com",
            "subject": "Exclusive 30% Off Back-to-School Dorm Essentials!",
            "body": "Huge Flash Sale! Use promo code DORM30 to get 30% off desk lamps, garment steamers, and noise-cancelling earbuds. Limited time offer ends Sunday!"
        },
        {
            "id": "sample-authentic-01",
            "title": "Authentic PayPal Payment Receipt",
            "sender": "service@paypal.com",
            "subject": "Receipt for your payment of $137.97 to PayPilot Demo Store",
            "body": "Hello College Student, you sent a payment of $137.97 USD to PayPilot Demo Store. Payment Confirmation ID: 9BT48291KL382. You can view your transaction history anytime in your account."
        },
        {
            "id": "sample-ambiguous-01",
            "title": "Unverified Delivery Notification (Needs Review)",
            "sender": "tracking-alerts@fastdelivery-global.net",
            "subject": "Package Delivery Update: Fee Pending",
            "body": "Your package delivery is held due to an unpaid $1.99 handling fee. Click here to confirm shipping address and release your parcel."
        }
    ]

    @classmethod
    def classify_message(
        cls,
        sender: str,
        subject: str,
        body: str
    ) -> Dict[str, Any]:
        """
        Classifies message text, identifies warning signs, and returns transparent explanations.
        """
        full_text = f"{sender} {subject} {body}".lower()
        warning_signs = []
        is_suspicious = False
        is_promotional = False
        is_important = False

        # 1. Check for Phishing / Suspicious Indicators
        for pat in cls.SUSPICIOUS_DOMAIN_PATTERNS:
            if re.search(pat, full_text):
                warning_signs.append("Suspicious domain link detected (resembles lookalike/spoofed domain)")
                is_suspicious = True

        for pat in cls.URGENCY_PATTERNS:
            if re.search(pat, full_text):
                warning_signs.append("Artificial high-urgency language attempting to compel immediate reaction")
                is_suspicious = True

        for pat in cls.CREDENTIAL_HARVEST_PATTERNS:
            if re.search(pat, full_text):
                warning_signs.append("Unsafe credential harvesting prompt (requesting PIN, OTP, password, or SSN)")
                is_suspicious = True

        # Check for unverified sender matching financial brand
        if "paypal" in (subject + body).lower() and not sender.endswith("@paypal.com"):
            warning_signs.append(f"Sender address '{sender}' is not an authentic @paypal.com domain")
            is_suspicious = True

        # 2. Check for Promotional Indicators
        for pat in cls.PROMOTIONAL_PATTERNS:
            if re.search(pat, full_text):
                is_promotional = True

        # 3. Check for Authentic Important Indicators
        for pat in cls.IMPORTANT_PATTERNS:
            if re.search(pat, full_text):
                is_important = True

        # 4. Determine Classification Category
        if is_suspicious:
            category = "SUSPICIOUS"
            risk_level = "HIGH"
            action_recommendation = (
                "Do NOT click any embedded links or share credentials. "
                "Verify your account status by navigating directly to PayPal.com through your browser."
            )
        elif is_important and not is_promotional:
            category = "IMPORTANT"
            risk_level = "LOW"
            action_recommendation = "Verified operational message. Kept for your records."
        elif is_promotional:
            category = "PROMOTIONAL"
            risk_level = "LOW"
            action_recommendation = "Commercial promotion or marketing newsletter. Safe to archive or ignore."
        else:
            category = "NEEDS_REVIEW"
            risk_level = "MEDIUM"
            warning_signs.append("Unrecognized sender or ambiguous delivery request")
            action_recommendation = "Review carefully. Confirm details through an official known portal."

        # Guardrails Transparency Disclosure
        disclaimer = (
            "Safety Guardrail Compliance: PayPilot Smart Filter provides heuristic warning guidance "
            "and does not claim definitive fraud detection. Messages are never silently deleted; "
            "the user retains full control to inspect or dismiss."
        )

        return {
            "category": category,
            "risk_level": risk_level,
            "sender": sender,
            "subject": subject,
            "warning_signs": warning_signs,
            "warning_count": len(warning_signs),
            "action_recommendation": action_recommendation,
            "silently_deleted": False,
            "guardrail_disclaimer": disclaimer
        }

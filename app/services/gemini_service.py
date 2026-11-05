
import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class GeminiService:
    MODEL = "gemini-3.8-flash"

    @classmethod
    def generate_reply(cls, user_message, deterministic_reply, bundle=None):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            print("GEMINI ERROR: API key not configured")
            return None

        trusted_data = {
            "deterministic_reply": deterministic_reply,
            "verified_bundle": bundle or {}
        }

        system_instruction = """
You are PayPilot AI, a budget-conscious shopping assistant.

Rules:
- Use only the supplied PayPilot data for product and price facts.
- Never invent prices, discounts, warranties or products.
- Never change verified budget calculations.
- Never claim a payment was completed or authorize a payment.
- PayPal handles all payment authorization and verification.
- Explain recommendations clearly and naturally.
- If information is missing, say so honestly.
"""

        prompt = f"""
User message:
{user_message}

Trusted PayPilot data:
{json.dumps(trusted_data, ensure_ascii=False)}

Existing assistant response:
{deterministic_reply}

Give the user a concise, natural and helpful response.
"""

        payload = {
            "model": cls.MODEL,
            "system_instruction": system_instruction,
            "input": prompt,
            "store": False,
            "generation_config": {
                "max_output_tokens": 350
            }
        }

        url = "https://generativelanguage.googleapis.com/v1beta/interactions"

        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            },
            method="POST"
        )

        import time

        for attempt in range(3):
            try:
                with urlopen(request, timeout=8) as response:
                    result = json.loads(response.read().decode("utf-8"))

                if result.get("status") != "completed":
                    print("GEMINI INCOMPLETE:", result.get("status"))
                    return None

                for step in result.get("steps", []):
                    if step.get("type") == "model_output":
                        for part in step.get("content", []):
                            if part.get("type") == "text" and part.get("text"):
                                print("GEMINI STATUS: SUCCESS")
                                return part["text"].strip()

                print("GEMINI ERROR: No text output found")
                return None

            except HTTPError as error:
                error_body = error.read().decode("utf-8")

                if error.code == 503 and attempt < 2:
                    print(f"GEMINI BUSY: Retry {attempt + 1}/2")
                    time.sleep(2 ** attempt)
                    continue

                print("GEMINI HTTP ERROR:", error.code)
                print("GEMINI RESPONSE:", error_body)
                return None

            except (URLError, TimeoutError, ValueError) as error:
                print("GEMINI CONNECTION ERROR:", str(error))
                return None

        return None

# PayPilot AI 2.0 — Setup and Environment Guide

> **Author / Module Owner**: Sehaj (Product Data, Comparison & Testing Lead)
> **Target Audience**: Team Members (Meenal, Jaskaran, Shubhneet, Suryansh) & Hackathon Evaluators
> **Repository**: Single Unified Monorepo (`/Paypal`)

---

## 1. System Requirements & Prerequisites

- **Python**: Version 3.10, 3.11, or 3.12 (Recommended for Flask backend & AI parsing)
- **Node.js**: Version 18+ (Optional: only if frontend build tooling or dev servers are used)
- **PowerShell / Bash**: Available on Windows, macOS, or Linux
- **PayPal Developer Account**: Sandbox access for client credentials ([developer.paypal.com](https://developer.paypal.com/))
- **Google AI Studio Key**: API key for Gemini 1.5 Flash ([aistudio.google.com](https://aistudio.google.com/))

---

## 2. Quickstart Installation (5 Minutes)

### Step 1: Clone and Enter Repository
```bash
git clone <repository-url>
cd Paypal
```

### Step 2: Configure Environment Variables
Copy `.env.example` to create your local `.env`:
```powershell
# Windows PowerShell:
Copy-Item .env.example .env

# Bash / Linux / macOS:
cp .env.example .env
```

Open `.env` and fill in your local sandbox keys:
```env
# Flask Server
FLASK_ENV=development
FLASK_PORT=5000
SECRET_KEY=super-secret-local-dev-key

# PayPal Sandbox (Owned by Suryansh)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret_here
PAYPAL_CURRENCY=USD

# Gemini AI (Owned by Shubhneet)
GEMINI_API_KEY=your_gemini_api_key_here
AI_MODEL_NAME=gemini-1.5-flash
```

> [!CAUTION]
> **Strict Security Guardrail**: Never commit `.env` or paste PayPal client secrets into public repositories or client-side code. All payment capture and credential storage must reside strictly on the server backend.

---

### Step 3: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Activate on macOS / Linux:
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

---

## 3. Running the Test Suite (Owned by Sehaj)

Before launching the servers or recording demos, verify that your environment passes all scenario guardrails and data validation tests.

### Option A: Standalone Zero-Dependency Runner (Windows PowerShell)
You can run the entire scenario test suite instantly without any external Python packages:
```powershell
powershell -ExecutionPolicy Bypass -File .\tests\run_tests.ps1
```
Expected output:
```text
======================================================================
 PAYPILOT AI 2.0 - HACKATHON TEST SUITE (POWERSHELL RUNNER)
 Owned by Sehaj (Product Data, Comparison & Testing Lead)
======================================================================

 [PASS] Catalogue JSON exists and is valid
 [PASS] All catalogue products carry explicit data_source & disclaimer
 [PASS] Dorm scenario optimal bundle arithmetic ($111.48 <= $150.00)
 [PASS] Over-budget dorm bundle is correctly flagged ($181.99 > $150.00)
 [PASS] Emergency laptop provides next-day delivery option and warranty
 [PASS] Price history carries simulated provenance and no unverified Honey claims
 [PASS] Order creation status 'CREATED' is not treated as payment completion
 [PASS] Captured order verifies COMPLETED status and exact amount ($111.48 USD)

======================================================================
 SUMMARY: Passed: 8 | Failed: 0
======================================================================
```

### Option B: Python Test Runner
```bash
python tests/test_runner.py
```
Or via pytest:
```bash
pytest -v tests/
```

---

## 4. Architecture & Team Module Endpoints

| Member | Primary Role | Core Files / Modules | Key API / Contract |
| :--- | :--- | :--- | :--- |
| **Meenal** | Frontend & UI | `frontend/`, `templates/`, `static/` | UI Components, product comparison cards, accessibility toggles |
| **Jaskaran** | Backend & Budget Guard | `app.py`, `routes/`, `utils/budget_guard.py` | `GET /api/products`, `POST /api/budget/evaluate` |
| **Shubhneet** | AI Chatbot & Intent Engine | `ai_service.py`, `prompts/` | `POST /api/chat/recommend` |
| **Suryansh** | PayPal Sandbox & Security | `paypal_service.py`, `routes/checkout.py` | `POST /api/paypal/create-order`, `POST /api/paypal/capture-order` |
| **Sehaj** | Data, Scenarios & Testing | `data/`, `tests/`, `utils/`, docs | Data provenance, bundle test fixtures, demo readiness |

---

## 5. PayPal Sandbox Setup Details (Lead: Suryansh)

1. Log in to [PayPal Developer Portal](https://developer.paypal.com/).
2. Navigate to **Dashboard > Apps & Credentials**.
3. Toggle to **Sandbox Mode** and click **Create App** (named `PayPilot-AI`).
4. Copy the generated **Client ID** and **Secret** to your `.env`.
5. Under **Sandbox > Accounts**, obtain credentials for:
   - **Personal Account**: Used by the buyer to approve orders during live demo.
   - **Business Account**: Merchant account receiving payments.
6. **Key Verification Rule**:
   - Order creation generates a token (`CREATED` status). **Do not treat this as payment.**
   - Buyer approval redirects to callback (`APPROVED` status). **Do not treat this as payment.**
   - Backend triggers PayPal Capture API (`/v2/checkout/orders/{id}/capture`). Only when status is **`COMPLETED`** does the app confirm payment.

---

## 6. Troubleshooting & FAQ

### Issue: "PowerShell script execution disabled on Windows"
**Fix**: Run PowerShell with execution policy bypass:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Issue: "Product data reports invalid provenance"
**Fix**: Ensure every product in `data/products.json` includes `data_source` and `data_source_disclaimer`. Run `python -m unittest tests.test_data_integrity` to pinpoint anomalies.

### Issue: "PayPal capture returns 401 Unauthorized"
**Fix**: Check that `PAYPAL_MODE=sandbox` and verify your client credentials in `.env` without surrounding quotation marks or whitespace.

# PayPilot AI 2.0 — AI Shopping Assistant, Intent Parser & Multi-Item Reasoning Engine
**PayPal AI Hackathon 2026** • *Module Owner: Jaskaran*

---

## 📌 Ownership & Work Division (From Hackathon Specification)

According to the official **PayPal AI Hackathon 2.0 Work Division**:
- **Member:** Jaskaran
- **Previous / Base Role:** Backend, Budget Guard, and AI reasoning engine.
- **Updated Responsibilities:** AI intent parsing, product ranking, recommendations and explanations; handle multi-constraint prompts and trade-offs across several items. Flask backend, trusted catalogue prices, and Budget Guard.
- **Key Change:** **Multi-item reasoning and Budget Guard are core deliverables.**

---

## 🚀 Key Deliverables Implemented by Jaskaran

### 1. 🧠 Multi-Constraint AI Intent Parser (`app/services/ai_intent_parser.py`)
- **Natural Language Entity Extraction**:
  - Automatically identifies product categories across rich synonym sets (`desk_lamp`, `portable_steamer`, `noise_cancelling_earbuds`, `laptop`, `medical_equipment`).
  - Extracts monetary budgets and strictness qualifiers (e.g., "$150 strict budget", "under 500 dollars").
  - Extracts user priority profiles (`reliability`, `cost`, `delivery_speed`, `warranty`).
  - Identifies situational context (`college_dorm`, `emergency_expense`, `general_shopping`).
  - Classifies intent types (`MULTI_ITEM_OPTIMIZATION`, `EMERGENCY_OPTIMIZATION`, `TRADE_OFF_QUERY`, `BUDGET_ADJUSTMENT`, `SWAP_REQUEST`, `CHECKOUT_INTENT`).

### 2. ⚡ Multi-Item Product Ranking Engine (`app/services/ai_ranking_engine.py` — Idea 10)
- **Cartesian Space Evaluation**: Evaluates combinations across requested product categories (e.g. 36 combinations for dorm items).
- **Multi-Factor Normalized Scoring**:
  $$Score = w_{\text{rel}} \cdot S_{\text{rel}} + w_{\text{cost}} \cdot S_{\text{cost}} + w_{\text{del}} \cdot S_{\text{del}} + w_{\text{war}} \cdot S_{\text{war}}$$
- **Automated Bundle Synthesis**:
  - **Top Recommended Bundle**: Optimal composite score strictly staying within the user's budget.
  - **Budget-Saver Bundle**: Minimum cost combination satisfying category needs.
  - **Premium Benchmark Bundle**: Highest reliability bundle (with transparent over-budget alert if it exceeds budget).
  - **Emergency Fast-Delivery Bundle**: Prioritizes 1-day turnaround and warranty coverage.

### 3. ⚖️ AI Trade-Off & Compromise Explainer (`app/services/ai_tradeoff_explainer.py`)
- **Deterministic Rationale Generation**:
  - Explains why TaoTronics ($32.99, ★ 9.2/10) was chosen over BenQ ($89.00) saving $56.01 to allow room for high-quality ANC earbuds.
  - Explains emergency laptop trade-offs: why Lenovo ThinkPad T14s Refurbished ($499.00, 1-day delivery, 12-month warranty) was selected over Acer Aspire 5 ($389.00, 2-day delivery) when time is critical.
  - **Over-Budget Shortfall Handler**: If a selected bundle exceeds budget, transparently reports the deficit and provides 1-click swap alternatives instead of hiding the shortfall.

### 4. 💬 Multi-Turn AI Conversational Assistant (`app/services/ai_conversational_assistant.py` — Idea 05)
- **Stateful Shopping Dialogue**:
  - Maintains conversation history, active bundle, active budget, and user preferences.
  - Handles trade-off questions ("Why didn't you choose the BenQ lamp?").
  - Dynamically re-optimizes when budget changes (e.g., lowering budget to $120 triggers dynamic swap to Hilife steamer while preserving ANC earbuds).
  - Handles item swaps and PayPal Sandbox checkout readiness checks.

### 5. 🎙️ Hands-Free Voice Commands Processor (`app/services/voice_command_service.py` — Idea 02)
- **Speech Intent Interpretation**: Maps spoken phrases to shopping and navigation actions.
- **Strict Safety Checklist Guardrail**:
  - Voice checkout commands **mandate explicit user confirmation** before any payment action (`requires_explicit_confirmation: True`).
  - Voice triggers cannot initiate money movement without affirmative consent.

### 6. 🛡️ Zero-Spam Financial Smart Filter (`app/services/financial_smart_filter.py` — Idea 07)
- **Financial Communication Classifier**: Classifies messages into `IMPORTANT`, `PROMOTIONAL`, `SUSPICIOUS`, or `NEEDS_REVIEW`.
- **Heuristic Warning Signs Analysis**: Flags lookalike domains (e.g. `paypa1-security-verification.xyz`), artificial urgency, and credential harvesting prompts.
- **Hackathon Checklist Compliance**:
  - Never silently deletes messages.
  - Never claims 100% definitive fraud detection.
  - Explains warning signs and safety recommendations transparently.

### 7. 🌐 Interactive Web UI (`web/index.html`, `web/styles.css`, `web/app.js`)
- Dedicated, sleek interface providing:
  - Multi-turn AI Shopping Chatbot with 1-click prompt chips and live Budget Guard side inspector.
  - Multi-Item Optimizer matrix comparing Recommended vs Budget Saver vs Premium bundles.
  - Hands-Free Voice Studio with Web Speech recognition and the payment confirmation modal.
  - Financial Smart Filter analyzer with pre-loaded realistic samples and custom message evaluator.

---

## 🛡️ Hackathon Accuracy and Safety Checklist Compliance

| Checklist Item | Jaskaran's Implementation |
| :--- | :--- |
| **No Hallucinated Math** | All bundle prices, totals, differences, and surplus buffers are computed through deterministic arithmetic from trusted catalogue records. |
| **PayPal Pay in 4 Disclosures** | The AI assistant explicitly discloses that Pay in 4 is subject to PayPal eligibility checks at checkout and that installment payments do not reduce total purchase obligation. |
| **Payment Verification Guardrail** | Voice command processor strictly enforces `requires_explicit_confirmation == True` on checkout actions; payment is never triggered solely by voice. |
| **Data Source Transparency** | Products carry verified retail benchmark labels (`Controlled Catalogue Price (Verified Retail Benchmark)`). |
| **No Silent Deletion of Messages** | Smart filter never deletes messages; tags them with risk levels and displays warning indicators. |
| **No Definitive Fraud Claims** | Smart filter explicitly includes disclosure that assessments are heuristic warning guidance. |

---

## 📡 REST API Reference (`/api/ai/*`)

### 1. `POST /api/ai/parse-intent`
Parses freeform prompt into structured parameters.
- **Request:** `{"prompt": "College student needing desk lamp, steamer, and study buds under $150. Prioritize reliability."}`
- **Response:**
```json
{
  "status": "success",
  "result": {
    "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
    "stated_budget": 150.0,
    "priority": "reliability",
    "context": "college_dorm",
    "intent_type": "MULTI_ITEM_OPTIMIZATION",
    "confidence_score": 1.0
  }
}
```

### 2. `POST /api/ai/recommend-bundle`
Multi-item budget optimization and ranking.
- **Request:**
```json
{
  "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
  "stated_budget": 150.0,
  "priority": "reliability"
}
```
- **Response:**
```json
{
  "status": "success",
  "stated_budget": 150.0,
  "priority": "reliability",
  "recommended_bundle": {
    "total_cost": 137.97,
    "surplus": 12.03,
    "average_reliability": 9.33,
    "is_within_budget": true,
    "items": [
      {"id": "lamp-taotronics-pro", "name": "TaoTronics Eye-Care Multi-Spectrum Desk Lamp", "price": 32.99},
      {"id": "steamer-conair-turbo", "name": "Conair Turbo ExtremeSteam Handheld Fabric Steamer", "price": 44.99},
      {"id": "buds-anker-space-a40", "name": "Anker Soundcore Space A40 Adaptive ANC Earbuds", "price": 59.99}
    ]
  },
  "budget_saver_bundle": {"total_cost": 68.97, "average_reliability": 8.1},
  "trade_off_explanations": [
    "Overall Strategy (Reliability Focus): Selected optimal combination totaling $137.97, leaving $12.03 surplus...",
    "In Desk Lamp: Chose 'TaoTronics Eye-Care Multi-Spectrum Desk Lamp' ($32.99) over 'BenQ' ($89.00) saving $56.01..."
  ]
}
```

### 3. `POST /api/ai/chat`
Multi-turn conversational assistant endpoint.
- **Request:** `{"session_id": "user_1", "message": "Why didn't you pick the BenQ lamp?"}`
- **Response:**
```json
{
  "status": "success",
  "reply_text": "We chose TaoTronics ($32.99) over BenQ ($89.00) saving $56.01 to allow room for high-quality ANC earbuds...",
  "intent": "TRADE_OFF_QUERY"
}
```

### 4. `POST /api/ai/voice-command`
Processes voice transcripts with safety checks.
- **Request:** `{"transcript": "Checkout with PayPal", "current_bundle_total": 137.97}`
- **Response:**
```json
{
  "status": "success",
  "result": {
    "interpreted_action": "INITIATE_PAYMENT",
    "requires_explicit_confirmation": true,
    "confirmation_prompt": "Security Guardrail: Voice commands require explicit verification before payment. Do you authorize initiating PayPal Sandbox checkout for $137.97?",
    "safety_checklist_rule": "Voice commands require explicit user confirmation before any payment action."
  }
}
```

### 5. `POST /api/ai/smart-filter`
Classifies financial communications.
- **Request:** `{"sender": "+18005550199", "subject": "Account suspended", "body": "Verify PIN at http://paypa1-security-verification.xyz"}`
- **Response:**
```json
{
  "status": "success",
  "result": {
    "category": "SUSPICIOUS",
    "risk_level": "HIGH",
    "warning_signs": ["Suspicious domain link detected", "Artificial urgency", "Credential harvesting"],
    "silently_deleted": false
  }
}
```

---

## 🧪 Testing & Validation

### Run Full Test Suite (58 Tests)
```bash
pytest -v
```
All **58 unit and integration tests** pass, validating:
- AI Intent Parsing across natural language prompts
- Multi-Constraint Bundle Optimization & Ranking
- Trade-Off Explanations & Shortfall Handling
- Conversational Chatbot & Budget Reductions
- Voice Command Processing & Safety Guardrails
- Financial Smart Filter & Warning Signs Detection
- REST API Integration contracts

### Run Standalone AI Demo
```bash
python demo_jaskaran_ai.py
```
Demonstrates all 5 hackathon scenarios in terminal output with complete trade-off explanations.

---

## 🤝 Team Integration Summary

| Team Member | Module | Integration with Jaskaran's AI Engine |
| :--- | :--- | :--- |
| **Jaskaran** (This Module) | Backend, Budget Guard & AI | Connects catalogue data and Budget Guard verification endpoints (`/api/products`, `/api/budget-guard/*`) with multi-item reasoning. |
| **Suryansh** | Frontend & PayPal Integration | Suryansh's UI consumes `/api/ai/*` endpoints for chatbot dialogue, trade-offs, voice input, and guides validated bundles into verified PayPal Sandbox checkout. |
| **Akashdeep** | Testing & QA Lead | Validates against test datasets, emergency expense flows, scenario tests, and open-source documentation. |

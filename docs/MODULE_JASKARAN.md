# PayPilot AI — Backend & Budget Guard Engine
**PayPal AI Hackathon 2026** • *PayPilot AI 2.0*

> **Module Owner:** Jaskaran (Flask Backend, Catalogue, Trusted Prices, Product/Bill APIs, Budget Guard Engine)

---

## 📌 Overview & Architecture

PayPilot AI is a budget-aware shopping assistant that pairs natural language needs with **zero-hallucination, deterministic budget verification** and PayPal checkout.

In accordance with the team work division:
- **Jaskaran (This Backend)**: Provides the single source of truth for catalogue data, trusted prices, bill records, server-locked order preparations, and mathematical **Budget Guard** calculations.
- **Meenal (Frontend)**: Consumes these endpoints to render shopping cards, bundle comparisons, accessibility controls, and checkout screens.
- **Shubhneet (AI Chatbot)**: Connects natural language intent parsing with the `/api/budget-guard/optimize-bundle` and `/api/products` endpoints to deliver ranked options and explain trade-offs.
- **Suryansh (PayPal Integration)**: Coordinates PayPal Sandbox checkout using `/api/orders/prepare` and server-side payment verification via `/api/orders/verify-capture`.
- **Sehaj (Testing & QA)**: Validates seed datasets, emergency-expense flows, and test suites.

---

## 🛡️ Hackathon Guardrails Compliance

- **No Hallucinated Math**: Budget Guard totals, differences, and tax/shipping computations are computed strictly through deterministic code against verified SQLite records.
- **Transparent Data-Source Labeling**: Every product returned by `/api/products` includes `data_source` and `data_source_label` (`Controlled Catalogue Price (Verified Retail Benchmark)`).
- **Simulated Honey Trends**: Price trends returned via `/api/products/<id>/price-history` explicitly disclose: `"Price trends are simulated sample movements for demonstration; not an active Honey API feed."`
- **Proactive Bill Tracking (Non-Invasive)**: Bill reminders operate strictly on user-entered records without falsely implying live bank account access.
- **Server-Side Payment Verification**: Orders are only promoted to `CAPTURED` after the backend verifies that the captured PayPal amount and currency match the locked catalogue total.

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.9+
- SQLite3

### 2. Environment Setup
```bash
# Clone and enter directory
cd "Paypal ai hackathon"

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### 3. Run the Backend Server
```bash
python run.py
```
The server will automatically initialize SQLite database tables (`paypilot.db`), seed verified product and bill records, and listen on **`http://127.0.0.1:5001`**.

### 4. Run the Test Suite
```bash
pytest -v
```
All 28 unit and integration tests validate the catalogue, Budget Guard calculations, dorm scenarios, emergency navigator, bills, and REST API routes.

---

## 📡 API Reference & Integration Contracts

### 1. Catalogue & Product APIs

#### `GET /api/products`
Fetch products with flexible filtering and sorting.
- **Query Params:**
  - `category` (string, optional): e.g. `desk_lamp`, `portable_steamer`, `noise_cancelling_earbuds`, `laptop`, `medical_equipment`
  - `search` (string, optional): Keyword search matching name, brand, or description
  - `min_price` / `max_price` (float, optional)
  - `sort_by` (string, optional): `price_asc`, `price_desc`, `reliability_desc`
  - `in_stock_only` (bool, optional, default `false`)
- **Response `200 OK`:**
```json
{
  "status": "success",
  "count": 10,
  "data_source_disclosure": "Controlled catalogue prices with verified retail benchmarks.",
  "products": [
    {
      "id": "lamp-taotronics-pro",
      "name": "TaoTronics Eye-Care Multi-Spectrum Desk Lamp",
      "category": "desk_lamp",
      "brand": "TaoTronics",
      "price": 32.99,
      "original_price": 39.99,
      "reliability_score": 9.2,
      "warranty_months": 24,
      "delivery_days": 1,
      "data_source": "curated_catalog_verified_retail",
      "data_source_label": "Controlled Catalogue Price (Verified Retail Benchmark)",
      "specs": {
        "brightness_lumens": 650,
        "color_modes": 5
      }
    }
  ]
}
```

#### `GET /api/products/<id>`
Fetch a single product by ID.

#### `GET /api/products/<id>/price-history`
Fetch price movement trends (with Honey simulation disclosure).

#### `GET /api/categories`
Summary list of all product categories with count and price ranges.

---

### 2. Budget Guard Engine APIs

#### `POST /api/budget-guard/check`
Calculates deterministic totals for a list of items and flags whether the bundle is within or over budget. Optionally factors in bills due within 7 days.
- **Request Body:**
```json
{
  "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
  "stated_budget": 150.00,
  "apply_tax": false,
  "apply_shipping": false,
  "include_bills": true,
  "bills_due_within_days": 7
}
```
- **Response `200 OK` (Under Budget):**
```json
{
  "status": "success",
  "result": {
    "stated_budget": 150.00,
    "currency": "USD",
    "calculation_basis": "deterministic_catalogue_lookup",
    "pricing_breakdown": {
      "subtotal": 137.97,
      "tax": 0.0,
      "shipping": 0.0,
      "total": 137.97
    },
    "status": "UNDER_BUDGET",
    "is_over_budget": false,
    "difference": 12.03,
    "amount_remaining": 12.03,
    "budget_utilization_percentage": 92.0,
    "average_reliability_score": 9.33,
    "status_message": "Bundle total $137.97 is within budget. You have $12.03 remaining.",
    "bill_awareness": {
      "upcoming_bills_total": 80.00,
      "disposable_budget_after_bills": 70.00,
      "is_over_disposable_budget": true,
      "advisory": "Warning: Upcoming bills ($80.00) due within 7 days leave an effective shopping balance of $70.00."
    }
  }
}
```

#### `POST /api/budget-guard/optimize-bundle`
**The Core Hackathon Demo Endpoint.** Evaluates combinations across requested categories and selects the optimal combination satisfying constraints and maximizing reliability.
- **Request Body:**
```json
{
  "categories": ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
  "stated_budget": 150.00,
  "priority": "reliability"
}
```
- **Response `200 OK`:**
```json
{
  "status": "success",
  "result": {
    "stated_budget": 150.00,
    "currency": "USD",
    "total_combinations_evaluated": 36,
    "feasible_combinations_count": 18,
    "recommended_bundle": {
      "label": "Best Fit (High Reliability Under Budget)",
      "is_within_budget": true,
      "total_cost": 137.97,
      "difference": 12.03,
      "average_reliability": 9.33,
      "items": [
        {"id": "lamp-taotronics-pro", "name": "TaoTronics Eye-Care...", "price": 32.99, "reliability_score": 9.2},
        {"id": "steamer-conair-turbo", "name": "Conair Turbo Extreme...", "price": 44.99, "reliability_score": 9.4},
        {"id": "buds-anker-space-a40", "name": "Anker Soundcore Space A40...", "price": 59.99, "reliability_score": 9.4}
      ]
    },
    "budget_saver_bundle": {
      "label": "Lowest Total Cost Option",
      "total_cost": 68.97,
      "average_reliability": 8.1
    },
    "trade_off_explanations": [
      "Selected optimal bundle staying strictly under $150.00. Total $137.97 leaves $12.03 surplus with an average reliability rating of 9.33/10.",
      "In Desk Lamp: Chose 'TaoTronics Eye-Care Multi-Spectrum Desk Lamp' ($32.99, 9.2/10) over 'BenQ e-Reading Architectural LED Task Light' ($89.00) saving $56.01 to protect the bundle budget."
    ]
  }
}
```

#### `POST /api/budget-guard/alternatives`
Suggests swap candidates when a selected bundle exceeds budget.
- **Request Body:**
```json
{
  "current_item_ids": ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"],
  "stated_budget": 150.00
}
```
- **Response `200 OK`:**
```json
{
  "status": "success",
  "result": {
    "is_over_budget": true,
    "current_cost": 193.98,
    "shortfall": 43.98,
    "viable_swaps": [
      {
        "type": "single_item_swap",
        "remove_item": {"id": "lamp-benq-eread", "name": "BenQ e-Reading...", "price": 89.00},
        "add_item": {"id": "lamp-taotronics-pro", "name": "TaoTronics...", "price": 32.99},
        "savings": 56.01,
        "new_bundle_total": 137.97,
        "new_surplus": 12.03,
        "trade_off_explanation": "Swap 'BenQ e-Reading...' ($89.00) for 'TaoTronics...' ($32.99). Saves $56.01, bringing total down to $137.97 ($12.03 under budget)."
      }
    ]
  }
}
```

---

### 3. Proactive Financial Health & Bill APIs

- `GET /api/bills`: List bills (supports `?due_within_days=7`)
- `POST /api/bills`: Create a bill record (`title`, `amount`, `due_date`, `category`, `recurring`)
- `PUT /api/bills/<id>`: Update bill record
- `DELETE /api/bills/<id>`: Delete bill record
- `GET /api/bills/summary?shopping_budget=150.00&days_window=7`: Summarizes bills due in 7 days and computes disposable shopping budget.

---

### 4. Order Preparation & PayPal Verification APIs (for Suryansh & Meenal)

#### `POST /api/orders/prepare`
Locks catalogue items and prices on the server, generating an order ID and PayPal Orders v2 payload.
- **Request Body:**
```json
{
  "item_ids": ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"],
  "stated_budget": 150.00
}
```
- **Response `201 Created`:**
```json
{
  "status": "success",
  "order": {
    "order_id": "PAYPILOT-B4E9A7102F",
    "currency": "USD",
    "total_amount": 137.97,
    "ready_for_paypal_checkout": true,
    "paypal_create_order_payload": {
      "intent": "CAPTURE",
      "purchase_units": [
        {
          "reference_id": "PAYPILOT-B4E9A7102F",
          "amount": {
            "currency_code": "USD",
            "value": "137.97",
            "breakdown": {
              "item_total": {"currency_code": "USD", "value": "137.97"},
              "tax_total": {"currency_code": "USD", "value": "0.00"},
              "shipping": {"currency_code": "USD", "value": "0.00"}
            }
          }
        }
      ]
    }
  }
}
```

#### `POST /api/orders/verify-capture`
Called after buyer approval and PayPal capture. Validates captured amount against server records before confirming payment.
- **Request Body:**
```json
{
  "order_id": "PAYPILOT-B4E9A7102F",
  "paypal_order_id": "8XY123456789",
  "captured_amount": 137.97,
  "captured_currency": "USD"
}
```
- **Response `200 OK` (Verified):**
```json
{
  "status": "success",
  "verification": {
    "verified": true,
    "order_id": "PAYPILOT-B4E9A7102F",
    "status": "CAPTURED",
    "captured_amount": 137.97,
    "message": "Payment verified and recorded successfully against server catalogue total."
  }
}
```
*(If the amount differs, returns `400 Bad Request` with `verified: false` and `VERIFICATION_FAILED`.)*

---

## 🧪 Demo Scenarios Covered

1. **The College Dorm Bundle ($150 Budget)**:
   - Evaluates Lamp + Steamer + Earbuds.
   - Recommended bundle: TaoTronics ($32.99) + Conair ($44.99) + Anker Space A40 ($59.99) = **$137.97** ($12.03 under budget, 9.33 avg reliability).
   - If BenQ ($89.00) is picked, Budget Guard flags **OVER_BUDGET ($193.98, $43.98 over)** and suggests the exact swap.
2. **Emergency Laptop & Urgent Replacement**:
   - Urgent Refurbished ThinkPad T14s ($499, 1-day delivery, 1-year warranty, 9.6 reliability) vs New Acer Aspire 5 ($389, 2-day delivery, 8.6 reliability).
3. **Proactive Financial Health (7-Day Bill Awareness)**:
   - 2 bills due in 7 days totaling **$80.00** (Dorm Electric $45 + WiFi $35).
   - Shows remaining disposable shopping budget: **$150 - $80 = $70.00**.

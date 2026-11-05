# PayPilot AI 2.0 — Frontend, Shopping UI & Accessibility
**PayPal AI Hackathon 2026** • *Module Owner: Meenal*

---

## 📌 Ownership & Work Division (From Hackathon Specification)

According to the official **PayPal AI Hackathon 2.0 Work Division**:
- **Member:** Meenal
- **Previous / Base Role:** Frontend/dashboard and accessibility.
- **Updated Responsibilities:** Frontend/dashboard, product cards, comparison, accessibility controls, and checkout screens; connect the UI to backend APIs and show multi-item bundle totals.
- **Key Change:** *Clear ownership of the full shopping UI and bundle comparison.*

---

## 🚀 Key Features Implemented by Meenal

### 1. 🛍️ Full Shopping UI & Core 4-Step User Journey
* **Step 1: Describe**
  * Natural language requirements input with 1-click demo scenario chips:
    * **College Dorm Move-In ($150 Strict Budget)**: Lamp + Steamer + Noise-Cancelling Earbuds.
    * **Emergency Broken Laptop Replacement ($500 Budget)**: Fast 1-day delivery and warranty focus.
  * Stated budget controls and optimization objective selection (`High Reliability` vs `Lowest Cost`).
* **Step 2: Compare**
  * **Product Cards**: Detailed cards showing retail benchmarks, reliability ratings (`★ 9.4/10`), delivery turnaround, warranty months, and controlled data source disclosure.
  * **Multi-Item Bundle Comparison Matrix**: Side-by-side comparison of **AI Recommended Bundle** ($137.97, 9.33 avg reliability) vs **Budget-Saver Bundle** ($68.97) vs Custom selection.
  * **Trade-Off Explanations**: Highlights why TaoTronics ($32.99) was chosen over BenQ ($89.00) to protect the student budget while maintaining high reliability.
* **Step 3: Check (Budget Guard Engine Integration)**
  * Deterministic calculation display: Stated Budget, Subtotal, Tax, Shipping, Final Total, and Utilization percentage.
  * **Under-Budget Status**: Green glowing banner displaying surplus funds (`+$12.03 remaining`).
  * **Over-Budget Detection & 1-Click Viable Swaps**: When budget is exceeded (e.g. if BenQ $89 lamp is chosen, total $193.98), flags **OVER BUDGET (-$43.98)** and generates 1-click swap alternatives that immediately fix the bundle.
* **Step 4: Pay (PayPal Sandbox Checkout Screens)**
  * **Stage 1 (Review & Lock)**: Calls `POST /api/orders/prepare` to lock catalogue prices against client-side tampering.
  * **Stage 2 (Sandbox Auth)**: Calls `POST /api/orders/<id>/create-paypal-order` to generate PayPal Sandbox order with `PENDING_APPROVAL` status.
  * **Stage 3 (Buyer Approval Simulation)**: Calls `POST /api/orders/<id>/simulate-approval`. Strictly enforces checklist rule: *Buyer approval is NOT treated as proof of payment.*
  * **Stage 4 (Server-Side Capture & Verification)**: Calls `POST /api/orders/<id>/capture`. Verifies that captured amount and currency match locked catalogue total before presenting confirmed receipt.

---

### 2. ♿ Adaptive Universal Accessibility (Idea 01)
* **High Contrast Mode (WCAG AAA)**: High-contrast theme (pitch black background `#000000`, high-contrast yellow `#ffff00` and cyan `#00ffff` accents, prominent borders) toggleable via button or `Alt+H`.
* **Scalable Typography**: Font size scaler cycling through **100% Standard**, **120% Medium**, and **140% Large** via button or `Alt+T`.
* **Keyboard Navigation & Clear Focus States**:
  * "Skip to main shopping content" link at page top.
  * Persistent 3px/4px focus outlines (`:focus-visible`).
  * Modal focus trapping with `Escape` key close.
  * Keyboard shortcut modal accessible via `Alt+K`.
* **Text-to-Speech (TTS) Engine**:
  * Built using Web Speech Synthesis API.
  * Dedicated "Read Aloud" button (`Alt+R`) to read aloud current recommendations, Budget Guard status, and AI trade-off explanations.
* **Screen Reader Live Announcements**: Dynamic announcements dispatched through dedicated `#sr-announcer` (`aria-live="polite"` and `aria-live="assertive"`).

---

### 3. 🎙️ Hands-Free Voice Commands (Idea 02)
* Implemented via Web Speech Recognition API (`webkitSpeechRecognition`).
* Visual transcript banner showing interpreted natural language requests.
* Supported voice commands:
  * *"College dorm move in"* / *"Optimize dorm"*
  * *"Emergency laptop"* / *"Broken laptop"*
  * *"Check budget"* / *"Recalculate"*
  * *"Toggle high contrast"* / *"Increase text size"*
  * *"Read summary"* / *"Stop speaking"*
  * *"Checkout"* / *"Pay"* (Triggers mandatory user confirmation modal before any payment action).

---

### 4. 📅 Proactive Financial Health & 7-Day Bills (Idea 03)
* Dedicated interactive Bill Tracker modal and budget callout.
* Shows user-recorded bills due within 7 days (e.g. Electric $45 + WiFi $35 = **$80.00**).
* Calculates **Safe Disposable Balance**: `$150.00 Budget - $80.00 Bills = $70.00 Disposable`.
* Transparent disclosure: *"Calculated from user-recorded bills. Live bank balance connections are not accessed."*

---

### 5. 🚨 Emergency Expense & Medical Bill Navigator (Idea 08)
* Dedicated emergency view for unexpected replacement items (e.g., broken work laptop under $500 budget).
* Compares **Lenovo ThinkPad T14s Refurbished** ($499.00, 1-day express delivery, 12mo warranty, 9.6 rating) vs **Acer Aspire 5** ($389.00, 2-day delivery, 8.6 rating).
* Highlights the critical trade-off: 1-day turnaround vs price savings.

---

### 6. 📈 PayPal Honey Price Trend & History Engine (Idea 06)
* Price history popup drawer showing simulated price movements.
* Mandatory Guardrail Disclosure: *"Price trends are simulated sample movements for demonstration; not an active Honey API feed."*

---

## 🛡️ Hackathon Accuracy and Safety Checklist Compliance

| Checklist Item | Meenal's Frontend Implementation |
| :--- | :--- |
| **Do not claim PayPal Pay in 4 is always available** | Displays installment estimate ($34.49 x 4) alongside mandatory notice: *"PayPal Pay in 4 is subject to consumer eligibility and credit checks by PayPal at checkout... It is not guaranteed."* |
| **Do not treat a small instalment as proof of affordability** | Emphasizes: *"Paying in 4 installments of $34.49 does not reduce your total financial obligation. The full cost remains $137.97."* |
| **Do not claim payment succeeded until backend verifies capture** | 4-stage checkout modal explicitly marks Stage 3 as `APPROVED_BY_BUYER` (NOT paid). Only advances to confirmed receipt after Stage 4 server-side mathematical verification. |
| **Label data sources transparently** | Every product card carries: `Controlled Catalogue Price (Verified Retail Benchmark)`. |
| **Do not store secrets on client** | Frontend uses zero secret keys or private credentials; calls server-side endpoints for all orders. |

---

## 📂 Project Structure

```
E:\Meenal_Work\
├── index.html                  # Main application UI & dashboard
├── serve.ps1                   # Local HTTP server script for development & demo
├── README.md                   # This documentation
├── css/
│   ├── styles.css              # PayPal design system, cards, grid, modals
│   └── accessibility.css       # High contrast theme, scalable typography, focus rings
├── js/
│   ├── config.js               # Application configuration & API endpoints
│   ├── catalogue_data.js       # Verified catalogue & simulated Honey trends
│   ├── api.js                  # Backend REST API client with local deterministic fallback
│   ├── accessibility.js        # Universal accessibility controller (TTS, contrast, scale)
│   ├── voice.js                # Speech recognition & hands-free voice commands
│   ├── bill_manager_ui.js      # 7-day bill tracker & disposable budget calculator
│   ├── budget_guard_ui.js      # Bundle comparison matrix & over-budget viable swaps
│   ├── paypal_checkout_ui.js   # 4-stage PayPal Sandbox checkout & Pay in 4 UI
│   └── app.js                  # Main application router & view manager
└── tests/
    ├── run_tests.html          # Interactive test runner
    └── test_meenal_work.js     # 10 comprehensive automated test suites
```

---

## 🚦 How to Run & Verify

### Option A: Open directly in Browser
Double-click `index.html` in your browser (Chrome, Edge, or Firefox). All features, including local deterministic Budget Guard calculations, work seamlessly out-of-the-box.

### Option B: Run Local HTTP Server
In PowerShell:
```powershell
cd E:\Meenal_Work
.\serve.ps1 -Port 3000
```
Open **`http://localhost:3000/index.html`** in your browser.

### Option C: Run Automated Tests
Open **`http://localhost:3000/tests/run_tests.html`** (or open `tests/run_tests.html` directly).
All 10 test suites validate:
1. Catalogue data & retail benchmarks
2. Honey simulated trends disclosure
3. College Dorm Move-In deterministic total ($137.97, $12.03 surplus)
4. Multi-item bundle optimization
5. Over-budget detection ($193.98) & 1-click BenQ ➔ TaoTronics swap ($56.01 savings)
6. 7-Day bills filter ($80.00 total) & disposable balance ($70.00)
7. Accessibility controls (High contrast, text scaling, ARIA announcer)
8. PayPal Sandbox 4-stage state machine (PREPARED ➔ PENDING_APPROVAL ➔ APPROVED ➔ CAPTURED)
9. Pay in 4 disclosures and mathematical division ($34.49 x 4)
10. Emergency laptop comparison (ThinkPad T14s 1-day delivery under $500)

/**
 * PayPilot AI — Automated Test Suite for Meenal's Work
 * Validates:
 * 1. Catalogue Data & Guardrail Disclosures
 * 2. Deterministic Budget Guard Calculations & Over-Budget Swaps
 * 3. Proactive Financial Health (7-Day Bill Awareness)
 * 4. Adaptive Universal Accessibility (High Contrast, Text Scale, Announcer)
 * 5. PayPal Sandbox Checkout Pipeline & Pay in 4 Disclosures
 * 6. Emergency Expense Navigator Comparison
 */

(function () {
  const tests = [];
  let passedCount = 0;
  let failedCount = 0;

  function describe(name, fn) {
    tests.push({ name, fn });
  }

  function assert(condition, message) {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  }

  function assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(`Expected [${expected}] but got [${actual}]. ${message || ''}`);
    }
  }

  function assertClose(actual, expected, delta = 0.01, message = "") {
    if (Math.abs(actual - expected) > delta) {
      throw new Error(`Expected ~[${expected}] (±${delta}) but got [${actual}]. ${message}`);
    }
  }

  // =========================================================================
  // TEST SUITE DEFINITIONS
  // =========================================================================

  describe("1. Catalogue Data & Benchmark Compliance", async () => {
    assert(window.VERIFIED_CATALOGUE && window.VERIFIED_CATALOGUE.length >= 9, "Catalogue should contain at least 9 verified products");

    window.VERIFIED_CATALOGUE.forEach(p => {
      assert(p.id, `Product missing id: ${p.name}`);
      assert(p.name, `Product missing name: ${p.id}`);
      assert(typeof p.price === "number" && p.price > 0, `Product missing valid price: ${p.id}`);
      assert(p.reliability_score >= 1 && p.reliability_score <= 10, `Product reliability out of range: ${p.id}`);
      assert(p.warranty_months > 0, `Product missing warranty: ${p.id}`);
      assert(p.delivery_days > 0, `Product missing delivery days: ${p.id}`);
      assert(p.data_source_label.includes("Controlled Catalogue Price"), `Missing required data source label for ${p.id}`);
    });
  });

  describe("2. Honey Price Trend Guardrail Disclosures", async () => {
    const lamp = window.VERIFIED_CATALOGUE.find(p => p.id === "lamp-taotronics-pro");
    assert(lamp && lamp.price_history && lamp.price_history.length > 0, "TaoTronics should have price history");

    const historyData = await window.api.getPriceHistory(lamp.id);
    assert(historyData.disclaimer.includes("simulated sample movements"), "Price history must contain simulated Honey disclaimer");
  });

  describe("3. Deterministic Dorm Move-In Calculation ($150 Budget)", async () => {
    const itemIds = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"];
    const result = await window.api.checkBudget(itemIds, 150.00);

    assertEqual(result.status, "UNDER_BUDGET", "Bundle should be under budget");
    assertEqual(result.is_over_budget, false, "is_over_budget should be false");
    assertClose(result.pricing_breakdown.subtotal, 137.97, 0.01, "Subtotal must equal 137.97");
    assertClose(result.pricing_breakdown.total, 137.97, 0.01, "Total must equal 137.97");
    assertClose(result.difference, 12.03, 0.01, "Surplus must equal 12.03");
    assertClose(result.budget_utilization_percentage, 92.0, 0.5, "Utilization must be ~92%");
    assertClose(result.average_reliability_score, 9.33, 0.05, "Avg reliability must be ~9.33");
  });

  describe("4. Multi-Item Bundle Optimization Engine", async () => {
    const opt = await window.api.optimizeBundle(
      ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],
      150.00,
      "reliability"
    );

    assert(opt.recommended_bundle, "Should return recommended bundle");
    assertEqual(opt.recommended_bundle.is_within_budget, true, "Recommended bundle must be within budget");
    assertClose(opt.recommended_bundle.total_cost, 137.97, 0.01, "Recommended bundle total must be 137.97");
    assert(opt.budget_saver_bundle, "Should return budget saver bundle");
    assertClose(opt.budget_saver_bundle.total_cost, 73.97, 6.0, "Budget saver total must be minimum (~68.97 - 73.97)");
    assert(opt.trade_off_explanations.length >= 2, "Must return trade-off explanations");
  });

  describe("5. Over-Budget Detection & 1-Click Viable Swaps", async () => {
    // Pick expensive BenQ lamp ($89.00)
    const overItemIds = ["lamp-benq-eread", "steamer-conair-turbo", "buds-anker-space-a40"];
    const result = await window.api.checkBudget(overItemIds, 150.00);

    assertEqual(result.status, "OVER_BUDGET", "Should detect over budget");
    assertEqual(result.is_over_budget, true, "is_over_budget should be true");
    assertClose(result.pricing_breakdown.total, 193.98, 0.01, "Total must be 193.98");
    assertClose(result.difference, 43.98, 0.01, "Shortfall must be 43.98");

    const alts = await window.api.getAlternatives(overItemIds, 150.00);
    assertEqual(alts.is_over_budget, true, "Alternatives should confirm over budget");
    assert(alts.viable_swaps.length > 0, "Must identify viable swap");

    const swap = alts.viable_swaps[0];
    assertEqual(swap.remove_item.id, "lamp-benq-eread", "Should recommend removing BenQ lamp");
    assertEqual(swap.add_item.id, "lamp-taotronics-pro", "Should recommend adding TaoTronics lamp");
    assertClose(swap.savings, 56.01, 0.01, "Savings should be 56.01");
    assertClose(swap.new_bundle_total, 137.97, 0.01, "New total should be 137.97");
  });

  describe("6. Proactive Financial Health & 7-Day Bills Awareness", async () => {
    const summary = await window.api.getBillsSummary(150.00, 7);
    assertEqual(summary.shopping_budget, 150.00, "Shopping budget should match");
    assertEqual(summary.window_days, 7, "Window should be 7 days");
    assertClose(summary.upcoming_bills_total, 80.00, 0.01, "Upcoming 7-day bills must total 80.00 ($45 electric + $35 WiFi)");
    assertClose(summary.disposable_budget, 70.00, 0.01, "Disposable budget must be 70.00 ($150 - $80)");
    assert(summary.disclaimer.includes("Live bank balance connections are not accessed"), "Must include disclaimer");
  });

  describe("7. Adaptive Universal Accessibility Controls", async () => {
    assert(window.a11y, "AccessibilityController must be initialized");

    // High contrast test
    const initialContrast = window.a11y.highContrast;
    const toggled = window.a11y.toggleHighContrast();
    assertEqual(toggled, !initialContrast, "High contrast should toggle boolean");
    assertEqual(document.documentElement.classList.contains("high-contrast"), toggled, "Class list must reflect high contrast state");

    // Toggle back
    window.a11y.toggleHighContrast();

    // Text scale test
    window.a11y.applyTextScale("120");
    assert(document.documentElement.classList.contains("text-scale-120"), "Should apply text-scale-120 class");
    window.a11y.applyTextScale("100");
    assert(document.documentElement.classList.contains("text-scale-100"), "Should reset to text-scale-100 class");

    // Announcer test
    window.a11y.announce("Test Announcement", "polite");
    const announcer = document.getElementById("sr-announcer");
    assert(announcer, "Screen reader announcer element must exist");
  });

  describe("8. PayPal Sandbox 4-Stage Secure Checkout Flow", async () => {
    const itemIds = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"];

    // Stage 1: Lock order
    const order = await window.api.prepareOrder(itemIds, 150.00);
    assert(order.order_id.startsWith("PAYPILOT-"), "Order ID must have PAYPILOT prefix");
    assertEqual(order.status, "PREPARED", "Initial state must be PREPARED");
    assertClose(order.total_amount, 137.97, 0.01, "Locked amount must be 137.97");

    // Stage 2: Create PayPal Sandbox order
    const pp = await window.api.createPayPalOrder(order.order_id);
    assertEqual(pp.status, "PENDING_APPROVAL", "Status must be PENDING_APPROVAL");
    assert(pp.approval_url.includes("sandbox.paypal.com"), "Approval URL must point to PayPal Sandbox");
    assert(pp.security_notice.includes("Not confirmed as paid until server captures"), "Must include payment guardrail notice");

    // Stage 3: Buyer approval simulation
    const approval = await window.api.simulateBuyerApproval(order.order_id);
    assertEqual(approval.status, "APPROVED_BY_BUYER", "Status must be APPROVED_BY_BUYER");
    assert(approval.security_notice.includes("this is NOT proof of payment"), "Must emphasize approval != payment");

    // Stage 4: Server capture & verification
    const capture = await window.api.captureOrder(order.order_id);
    assertEqual(capture.status, "CAPTURED", "Status must be CAPTURED");
    assertEqual(capture.verified, true, "Order must be verified by backend");
    assertClose(capture.captured_amount, 137.97, 0.01, "Captured amount must match locked order");
  });

  describe("9. PayPal Pay in 4 Disclosures & Calculations", async () => {
    const itemIds = ["lamp-taotronics-pro", "steamer-conair-turbo", "buds-anker-space-a40"];
    const order = await window.api.prepareOrder(itemIds, 150.00);
    const p4 = await window.api.getPayIn4Estimate(order.order_id);

    assertEqual(p4.installment_count, 4, "Must have 4 installments");
    assertClose(p4.installment_amount, 34.49, 0.02, "Installment must be $34.49 (137.97 / 4)");
    assert(p4.affordability_warning.includes("does not reduce your total financial obligation"), "Must include affordability notice");
    assert(p4.eligibility_disclaimer.includes("subject to consumer eligibility"), "Must include eligibility disclaimer");
  });

  describe("10. Emergency Expense Navigator ($500 Laptop Scenario)", async () => {
    const laptops = await window.api.getProducts({ category: "laptop" });
    const thinkpad = laptops.find(l => l.id === "laptop-lenovo-t14s");

    assert(thinkpad, "Lenovo ThinkPad T14s must exist in catalogue");
    assertEqual(thinkpad.price, 499.00, "ThinkPad price must be $499.00");
    assertEqual(thinkpad.delivery_days, 1, "ThinkPad must offer 1-day express delivery");
    assertEqual(thinkpad.warranty_months, 12, "ThinkPad must offer 12-month warranty");
    assert(thinkpad.reliability_score >= 9.5, "ThinkPad must have high reliability score >= 9.5");
  });

  // =========================================================================
  // RUNNER
  // =========================================================================
  window.runMeenalTestSuite = async function () {
    const outputEl = document.getElementById("test-results-output");
    if (outputEl) outputEl.innerHTML = `<p>Running ${tests.length} test suites...</p>`;

    passedCount = 0;
    failedCount = 0;
    const results = [];

    for (const t of tests) {
      try {
        await t.fn();
        passedCount++;
        results.push({ name: t.name, passed: true });
      } catch (err) {
        failedCount++;
        results.push({ name: t.name, passed: false, error: err.message });
      }
    }

    if (outputEl) {
      outputEl.innerHTML = `
        <div style="padding: 16px; border-radius: 8px; margin-bottom: 20px; background: ${failedCount === 0 ? '#dcfce7' : '#fee2e2'}; border: 2px solid ${failedCount === 0 ? '#22c55e' : '#ef4444'};">
          <h2 style="color: ${failedCount === 0 ? '#15803d' : '#991b1b'}; margin-bottom: 6px;">
            ${failedCount === 0 ? '✅ All Tests Passed!' : '❌ Some Tests Failed'}
          </h2>
          <p style="font-weight: 600;">Passed: ${passedCount} / ${tests.length} Suites</p>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          ${results.map(r => `
            <div style="padding: 12px; border-radius: 6px; background: ${r.passed ? '#f0fdf4' : '#fef2f2'}; border: 1px solid ${r.passed ? '#86efac' : '#fca5a5'};">
              <strong>${r.passed ? '✓' : '✗'} ${r.name}</strong>
              ${r.error ? `<pre style="color: #b91c1c; margin-top: 6px; font-size: 12px;">${r.error}</pre>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }

    return { passedCount, failedCount, total: tests.length };
  };

  window.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("test-results-output")) {
      window.runMeenalTestSuite();
    }
  });
})();

/**
 * PayPilot AI — Budget Guard & Multi-Item Bundle Comparison UI
 * Module: Meenal (Shopping UI & Bundle Comparison Owner)
 *
 * Core Responsibilities:
 * 1. Multi-item basket management across categories (Lamp, Steamer, Earbuds, Laptops)
 * 2. Side-by-side bundle comparison (Recommended vs Budget-Saver vs Custom)
 * 3. Deterministic Budget Guard status, utilization gauge, and surplus/shortfall banner
 * 4. Transparent data source labels on every product card
 * 5. One-click Viable Swaps banner when bundle exceeds budget
 * 6. AI trade-off explanations presentation
 */

class BudgetGuardUI {
  constructor(apiClient = window.api) {
    this.api = apiClient;
    this.selectedItemIds = [
      "lamp-taotronics-pro",
      "steamer-conair-turbo",
      "buds-anker-space-a40"
    ];
    this.statedBudget = CONFIG.DEFAULT_DORM_BUDGET;
    this.lastCalculation = null;
    this.optimizationResult = null;
  }

  async init() {
    await this.runOptimization();
  }

  setStatedBudget(amount) {
    this.statedBudget = parseFloat(amount) || 0;
    this.recalculateCurrentBundle();
    if (window.billManagerUI) {
      window.billManagerUI.updateBudgetCardCallout(this.statedBudget);
    }
  }

  // -------------------------------------------------------------------------
  // 1. RUN OPTIMIZATION & RENDER COMPARISON
  // -------------------------------------------------------------------------
  async runOptimization(categories = CONFIG.DEFAULT_DORM_CATEGORIES, priority = "reliability") {
    this.showLoading(true);
    try {
      this.optimizationResult = await this.api.optimizeBundle(categories, this.statedBudget, priority);

      // Auto-select recommended bundle items
      if (this.optimizationResult.recommended_bundle && this.optimizationResult.recommended_bundle.items) {
        this.selectedItemIds = this.optimizationResult.recommended_bundle.items.map(i => i.id);
      }

      this.renderBundleComparisonMatrix();
      this.renderTradeOffExplanations();
      await this.recalculateCurrentBundle();
    } catch (err) {
      console.error("Optimization error:", err);
    } finally {
      this.showLoading(false);
    }
  }

  // -------------------------------------------------------------------------
  // 2. RECALCULATE BUDGET GUARD TOTALS
  // -------------------------------------------------------------------------
  async recalculateCurrentBundle() {
    try {
      const result = await this.api.checkBudget(this.selectedItemIds, this.statedBudget);
      this.lastCalculation = result;
      this.renderBudgetGuardBanner(result);
      this.renderSelectedItemsList();

      if (result.is_over_budget) {
        await this.renderViableSwaps();
      } else {
        const swapsContainer = document.getElementById("viable-swaps-container");
        if (swapsContainer) swapsContainer.innerHTML = "";
      }

      if (window.a11y) {
        window.a11y.announce(result.status_message, result.is_over_budget ? "assertive" : "polite");
      }
    } catch (err) {
      console.error("Budget check error:", err);
    }
  }

  // -------------------------------------------------------------------------
  // 3. RENDER BUDGET GUARD STATUS BANNER
  // -------------------------------------------------------------------------
  renderBudgetGuardBanner(result) {
    const banner = document.getElementById("budget-guard-banner");
    if (!banner) return;

    const isOver = result.is_over_budget;
    const bd = result.pricing_breakdown;
    const utilization = Math.min(100, result.budget_utilization_percentage);

    banner.className = `budget-guard-banner ${isOver ? 'banner-over-budget' : 'banner-under-budget'}`;
    banner.innerHTML = `
      <div class="banner-header">
        <div class="status-indicator">
          <span class="status-icon">${isOver ? '⚠️' : '✅'}</span>
          <div>
            <h3 class="status-title">${isOver ? 'OVER BUDGET DETECTED' : 'BUDGET GUARD VERIFIED: WITHIN BUDGET'}</h3>
            <p class="status-subtitle">${result.status_message}</p>
          </div>
        </div>
        <div class="status-badge-box">
          <span class="badge ${isOver ? 'badge-danger' : 'badge-success'}">
            ${isOver ? `Shortfall: -$${result.difference.toFixed(2)}` : `Surplus: +$${result.amount_remaining.toFixed(2)}`}
          </span>
        </div>
      </div>

      <div class="banner-body">
        <div class="budget-stat">
          <span class="stat-label">Stated Budget</span>
          <strong class="stat-value">$${result.stated_budget.toFixed(2)}</strong>
        </div>
        <div class="budget-stat">
          <span class="stat-label">Items Subtotal</span>
          <strong class="stat-value">$${bd.subtotal.toFixed(2)}</strong>
        </div>
        <div class="budget-stat">
          <span class="stat-label">Tax & Shipping</span>
          <strong class="stat-value">$${(bd.tax + bd.shipping).toFixed(2)}</strong>
        </div>
        <div class="budget-stat stat-highlight">
          <span class="stat-label">Bundle Total</span>
          <strong class="stat-value total-value">$${bd.total.toFixed(2)}</strong>
        </div>
        <div class="budget-stat">
          <span class="stat-label">Avg. Reliability</span>
          <strong class="stat-value rating-stars">★ ${result.average_reliability_score}/10</strong>
        </div>
      </div>

      <div class="budget-progress-container" aria-label="Budget utilization progress">
        <div class="progress-bar-track">
          <div class="progress-bar-fill ${isOver ? 'fill-over' : 'fill-safe'}" style="width: ${utilization}%"></div>
        </div>
        <div class="progress-labels">
          <span>0%</span>
          <span>${result.budget_utilization_percentage}% of $${result.stated_budget.toFixed(2)} budget</span>
          <span>100%</span>
        </div>
      </div>

      ${result.bill_awareness ? `
        <div class="banner-bill-alert ${result.bill_awareness.is_over_disposable_budget ? 'bill-warning' : 'bill-ok'}">
          <span class="icon">📅</span>
          <span>${result.bill_awareness.advisory}</span>
        </div>
      ` : ''}
    `;
  }

  // -------------------------------------------------------------------------
  // 4. RENDER VIABLE SWAPS (Over-budget recovery)
  // -------------------------------------------------------------------------
  async renderViableSwaps() {
    const container = document.getElementById("viable-swaps-container");
    if (!container) return;

    const alts = await this.api.getAlternatives(this.selectedItemIds, this.statedBudget);
    if (!alts.viable_swaps || alts.viable_swaps.length === 0) {
      container.innerHTML = `
        <div class="swap-callout-box">
          <h4>💡 Alternative Suggestion</h4>
          <p>No single-item swap brings this bundle under $${this.statedBudget.toFixed(2)}. Consider increasing your budget or switching to the Budget-Saver Bundle.</p>
          <button class="btn btn-secondary btn-sm" onclick="budgetGuardUI.selectBudgetSaverBundle()">
            Switch to Budget-Saver Bundle ($${this.optimizationResult?.budget_saver_bundle?.total_cost || '68.97'})
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="swap-callout-box alert-warning-theme">
        <div class="swap-callout-header">
          <h4>🔄 Budget Guard Recommendation: 1-Click Viable Swap</h4>
          <span class="shortfall-tag">Need to save $${alts.shortfall.toFixed(2)}</span>
        </div>
        <p class="swap-intro">Apply this verified catalogue swap to bring your bundle safely under budget without compromising critical features:</p>

        <div class="swaps-grid">
          ${alts.viable_swaps.map((swap, idx) => `
            <div class="swap-card">
              <div class="swap-comparison">
                <div class="swap-from">
                  <span class="swap-badge-red">Remove</span>
                  <strong>${swap.remove_item.name}</strong>
                  <span class="swap-price">$${swap.remove_item.price.toFixed(2)}</span>
                </div>
                <div class="swap-arrow">➔</div>
                <div class="swap-to">
                  <span class="swap-badge-green">Add</span>
                  <strong>${swap.add_item.name}</strong>
                  <span class="swap-price">$${swap.add_item.price.toFixed(2)}</span>
                </div>
              </div>
              <p class="swap-explanation">${swap.trade_off_explanation}</p>
              <div class="swap-action-row">
                <span class="savings-tag">Saves $${swap.savings.toFixed(2)} • New Total: $${swap.new_bundle_total.toFixed(2)}</span>
                <button class="btn btn-success btn-sm" onclick="budgetGuardUI.applySwap('${swap.remove_item.id}', '${swap.add_item.id}')">
                  ⚡ Apply Swap Now
                </button>
              </div>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  applySwap(removeId, addId) {
    this.selectedItemIds = this.selectedItemIds.filter(id => id !== removeId);
    this.selectedItemIds.push(addId);
    this.recalculateCurrentBundle();
    if (window.a11y) {
      window.a11y.announce("Swap applied successfully. Bundle is now under budget.", "assertive");
    }
  }

  // -------------------------------------------------------------------------
  // 5. RENDER BUNDLE COMPARISON MATRIX
  // -------------------------------------------------------------------------
  renderBundleComparisonMatrix() {
    const container = document.getElementById("bundle-comparison-matrix");
    if (!container || !this.optimizationResult) return;

    const rec = this.optimizationResult.recommended_bundle;
    const sav = this.optimizationResult.budget_saver_bundle;

    container.innerHTML = `
      <div class="comparison-column card ${rec.is_within_budget ? 'highlight-card' : ''}">
        <div class="col-header">
          <span class="pill-badge pill-blue">AI Recommended</span>
          <h3>Best Fit (High Reliability)</h3>
          <p class="col-subtitle">Maximizes durability & specs within stated budget</p>
          <div class="col-price">
            <span class="price-val">$${rec.total_cost.toFixed(2)}</span>
            <span class="badge ${rec.is_within_budget ? 'badge-success' : 'badge-danger'}">
              ${rec.is_within_budget ? `$${rec.difference.toFixed(2)} under budget` : 'Over budget'}
            </span>
          </div>
          <div class="col-reliability">
            <span>Average Reliability:</span> <strong>★ ${rec.average_reliability}/10</strong>
          </div>
        </div>
        <div class="col-items">
          ${(rec.items || []).map(item => `
            <div class="col-item-row">
              <span class="item-name">${item.name}</span>
              <span class="item-price">$${item.price.toFixed(2)}</span>
            </div>
          `).join("")}
        </div>
        <div class="col-action">
          <button class="btn btn-primary btn-block" onclick="budgetGuardUI.selectBundle('${(rec.items || []).map(i => i.id).join(",")}')">
            Select Recommended Bundle
          </button>
        </div>
      </div>

      <div class="comparison-column card">
        <div class="col-header">
          <span class="pill-badge pill-gray">Budget Saver</span>
          <h3>Lowest Total Cost</h3>
          <p class="col-subtitle">Strict minimum spending across all categories</p>
          <div class="col-price">
            <span class="price-val">$${sav.total_cost.toFixed(2)}</span>
            <span class="badge badge-success">
              $${(this.statedBudget - sav.total_cost).toFixed(2)} surplus
            </span>
          </div>
          <div class="col-reliability">
            <span>Average Reliability:</span> <strong>★ ${sav.average_reliability}/10</strong>
          </div>
        </div>
        <div class="col-items">
          ${(sav.items || []).map(item => `
            <div class="col-item-row">
              <span class="item-name">${item.name}</span>
              <span class="item-price">$${item.price.toFixed(2)}</span>
            </div>
          `).join("")}
        </div>
        <div class="col-action">
          <button class="btn btn-outline btn-block" onclick="budgetGuardUI.selectBundle('${(sav.items || []).map(i => i.id).join(",")}')">
            Select Budget Saver Bundle
          </button>
        </div>
      </div>
    `;
  }

  selectBundle(idString) {
    this.selectedItemIds = idString.split(",");
    this.recalculateCurrentBundle();
  }

  selectBudgetSaverBundle() {
    if (this.optimizationResult?.budget_saver_bundle?.items) {
      this.selectedItemIds = this.optimizationResult.budget_saver_bundle.items.map(i => i.id);
      this.recalculateCurrentBundle();
    }
  }

  // -------------------------------------------------------------------------
  // 6. RENDER TRADE-OFF EXPLANATIONS
  // -------------------------------------------------------------------------
  renderTradeOffExplanations() {
    const box = document.getElementById("tradeoff-explanation-box");
    if (!box || !this.optimizationResult) return;

    const explanations = this.optimizationResult.trade_off_explanations || [];
    box.innerHTML = `
      <div class="tradeoff-card">
        <div class="tradeoff-header">
          <span class="icon">🤖</span>
          <h4>AI Trade-Off & Multi-Constraint Reasoning</h4>
          <button class="btn btn-ghost btn-sm" onclick="a11y.readElement('tradeoff-content')">
            🔊 Read Explanations
          </button>
        </div>
        <div id="tradeoff-content" class="tradeoff-content">
          ${explanations.map(exp => `
            <div class="tradeoff-bullet">
              <span class="bullet-icon">💡</span>
              <p>${exp}</p>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  // -------------------------------------------------------------------------
  // 7. RENDER SELECTED ITEMS LIST
  // -------------------------------------------------------------------------
  renderSelectedItemsList() {
    const list = document.getElementById("selected-items-list");
    if (!list) return;

    const items = this.selectedItemIds.map(id => VERIFIED_CATALOGUE.find(p => p.id === id)).filter(Boolean);

    list.innerHTML = items.map(item => `
      <div class="selected-item-pill">
        <span class="item-cat-tag">${item.category_label || item.category}</span>
        <strong class="item-title">${item.name}</strong>
        <span class="item-cost">$${item.price.toFixed(2)}</span>
        <button class="btn-remove-item" onclick="budgetGuardUI.removeItem('${item.id}')" title="Remove item" aria-label="Remove ${item.name} from bundle">
          ✕
        </button>
      </div>
    `).join("");
  }

  removeItem(id) {
    this.selectedItemIds = this.selectedItemIds.filter(i => i !== id);
    this.recalculateCurrentBundle();
  }

  addItem(id) {
    if (!this.selectedItemIds.includes(id)) {
      this.selectedItemIds.push(id);
      this.recalculateCurrentBundle();
    }
  }

  showLoading(isLoading) {
    const spinner = document.getElementById("bundle-loading-spinner");
    if (spinner) {
      spinner.classList.toggle("hidden", !isLoading);
    }
  }
}

// Global instance
const budgetGuardUI = new BudgetGuardUI();
if (typeof window !== "undefined") {
  window.budgetGuardUI = budgetGuardUI;
}

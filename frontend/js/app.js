/**
 * PayPilot AI — Main Application Controller
 * Module: Meenal (Frontend / Dashboard & User Journey Integration)
 *
 * Implements:
 * 1. View routing (Dorm MVP Demo, Emergency Navigator, Catalogue, Comparison, Bills)
 * 2. Product catalogue browsing, search, and category filtering
 * 3. Product cards with verified data source disclosures and Honey price trends
 * 4. Quick-fill demo scenario handlers (College Dorm $150 & Emergency Laptop $500)
 * 5. Backend connection monitoring & health status pill
 */

class PayPilotApp {
  constructor() {
    this.currentView = "dorm"; // "dorm", "emergency", "catalogue", "comparison"
    this.allProducts = [];
    this.activeCategoryFilter = "all";
    this.searchTerm = "";
    this.activeSort = "reliability_desc";
  }

  async init() {
    // 1. Probe backend health
    window.api.onStatusChange((isOnline, message) => {
      this.updateConnectionStatusBadge(isOnline, message);
    });
    await window.api.probeBackend();

    // 2. Fetch products
    this.allProducts = await window.api.getProducts();

    // 3. Initialize components
    if (window.budgetGuardUI) await window.budgetGuardUI.init();
    if (window.billManagerUI) await window.billManagerUI.init();

    // 4. Render catalogue view
    this.renderCatalogueCards();

    // 5. Setup event listeners
    this.setupEventListeners();
  }

  // -------------------------------------------------------------------------
  // 1. SCENARIO LOADERS (MVP DEMOS)
  // -------------------------------------------------------------------------
  loadDormScenario() {
    this.switchView("dorm");
    const budgetInput = document.getElementById("stated-budget-input");
    const promptInput = document.getElementById("user-prompt-input");

    if (budgetInput) budgetInput.value = "150.00";
    if (promptInput) {
      promptInput.value = "I'm a college student moving into an unfurnished dorm with a strict $150 total budget. I need a desk lamp, a portable steamer, and noise-cancelling study buds. Prioritize reliability and explain compromises.";
    }

    if (window.budgetGuardUI) {
      window.budgetGuardUI.statedBudget = 150.00;
      window.budgetGuardUI.runOptimization(["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"], "reliability");
    }

    if (window.a11y) {
      window.a11y.announce("Loaded College Dorm Move-In demo ($150 budget). Analyzing optimal bundle...", "polite");
    }
  }

  loadEmergencyScenario() {
    this.switchView("emergency");
    const budgetInput = document.getElementById("emergency-budget-input");
    const promptInput = document.getElementById("emergency-prompt-input");

    if (budgetInput) budgetInput.value = "500.00";
    if (promptInput) {
      promptInput.value = "My work laptop suddenly died before project submission. Strict $500 maximum budget. Need fastest delivery and proven durability with warranty.";
    }

    this.renderEmergencyNavigator();

    if (window.a11y) {
      window.a11y.announce("Loaded Emergency Expense Navigator ($500 budget). Comparing rapid replacement laptops...", "polite");
    }
  }

  // -------------------------------------------------------------------------
  // 2. VIEW SWITCHING
  // -------------------------------------------------------------------------
  switchView(viewName) {
    this.currentView = viewName;
    document.querySelectorAll(".view-section").forEach(sec => sec.classList.add("hidden"));
    document.querySelectorAll(".nav-tab-btn").forEach(btn => btn.classList.remove("active"));

    const targetSec = document.getElementById(`view-${viewName}`);
    const targetBtn = document.getElementById(`nav-btn-${viewName}`);
    if (targetSec) targetSec.classList.remove("hidden");
    if (targetBtn) targetBtn.classList.add("active");

    if (viewName === "catalogue") {
      this.renderCatalogueCards();
    } else if (viewName === "emergency") {
      this.renderEmergencyNavigator();
    }
  }

  // -------------------------------------------------------------------------
  // 3. PRODUCT CATALOGUE CARDS & RENDERING
  // -------------------------------------------------------------------------
  async renderCatalogueCards() {
    const grid = document.getElementById("catalogue-cards-grid");
    if (!grid) return;

    let products = await window.api.getProducts({
      category: this.activeCategoryFilter === "all" ? "" : this.activeCategoryFilter,
      search: this.searchTerm,
      sort_by: this.activeSort
    });

    if (products.length === 0) {
      grid.innerHTML = `<div class="empty-state">No products found matching filters.</div>`;
      return;
    }

    grid.innerHTML = products.map(product => {
      const isSelected = window.budgetGuardUI && window.budgetGuardUI.selectedItemIds.includes(product.id);
      return `
        <div class="product-card card ${isSelected ? 'card-selected' : ''}" id="prod-card-${product.id}">
          <div class="card-media">
            <img src="${product.image_url}" alt="${this.escapeHtml(product.name)}" class="product-img" loading="lazy" />
            <span class="category-pill">${product.category_label || product.category}</span>
            ${product.original_price > product.price ? `
              <span class="discount-pill">Save $${(product.original_price - product.price).toFixed(2)}</span>
            ` : ''}
          </div>

          <div class="card-content">
            <div class="brand-row">
              <span class="brand-label">${this.escapeHtml(product.brand)}</span>
              <span class="reliability-badge">
                <span class="star">★</span> ${product.reliability_score}/10 Reliability
              </span>
            </div>

            <h3 class="product-title">${this.escapeHtml(product.name)}</h3>
            <p class="product-description">${this.escapeHtml(product.description)}</p>

            <div class="specs-preview">
              <span class="spec-tag">⏱️ ${product.delivery_days}-Day Delivery</span>
              <span class="spec-tag">🛡️ ${product.warranty_months}mo Warranty</span>
              <span class="spec-tag">📦 ${product.stock_quantity} in stock</span>
            </div>

            <div class="data-source-disclosure">
              <small>🏷️ ${product.data_source_label || 'Controlled Catalogue Price (Verified Retail Benchmark)'}</small>
            </div>

            <div class="card-pricing-row">
              <div class="price-box">
                <span class="current-price">$${product.price.toFixed(2)}</span>
                ${product.original_price ? `<span class="original-price">$${product.original_price.toFixed(2)}</span>` : ''}
              </div>
              <button class="btn btn-ghost btn-xs" onclick="app.openPriceHistoryModal('${product.id}')" title="View price trends">
                📈 Price Trend
              </button>
            </div>

            <div class="card-action-row">
              <button class="btn ${isSelected ? 'btn-danger' : 'btn-primary'} btn-block" onclick="app.toggleItemInBundle('${product.id}')">
                ${isSelected ? '✕ Remove from Bundle' : '+ Add to Bundle'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  toggleItemInBundle(productId) {
    if (!window.budgetGuardUI) return;
    if (window.budgetGuardUI.selectedItemIds.includes(productId)) {
      window.budgetGuardUI.removeItem(productId);
      if (window.a11y) window.a11y.announce("Item removed from bundle", "polite");
    } else {
      window.budgetGuardUI.addItem(productId);
      if (window.a11y) window.a11y.announce("Item added to bundle", "polite");
    }
    this.renderCatalogueCards();
  }

  // -------------------------------------------------------------------------
  // 4. PRICE HISTORY & SIMULATED HONEY TRENDS MODAL
  // -------------------------------------------------------------------------
  async openPriceHistoryModal(productId) {
    const modal = document.getElementById("price-history-modal");
    const content = document.getElementById("price-history-content");
    if (!modal || !content) return;

    modal.classList.remove("hidden");
    content.innerHTML = `<div class="spinner"></div><p>Loading price trends...</p>`;

    const historyData = await window.api.getPriceHistory(productId);

    content.innerHTML = `
      <div class="history-modal-body">
        <h3>${this.escapeHtml(historyData.product_name)}</h3>
        <p class="history-current">Current Verified Price: <strong>$${parseFloat(historyData.current_price).toFixed(2)}</strong></p>

        <div class="history-timeline">
          ${(historyData.history || []).map(h => `
            <div class="history-point">
              <span class="history-date">${h.date}</span>
              <span class="history-bar" style="width: ${Math.min(100, (h.price / 100) * 80)}%"></span>
              <strong class="history-val">$${parseFloat(h.price).toFixed(2)}</strong>
            </div>
          `).join("")}
        </div>

        <div class="honey-disclosure-box alert-warning-theme">
          <span class="icon">ℹ️</span>
          <div>
            <strong>Mandatory Guardrail Disclosure:</strong>
            <p>${historyData.disclaimer || 'Price trends are simulated sample movements for demonstration; not an active Honey API feed.'}</p>
          </div>
        </div>
      </div>
    `;

    if (window.a11y) {
      window.a11y.announce(`Opened price history for ${historyData.product_name}`, "polite");
    }
  }

  // -------------------------------------------------------------------------
  // 5. EMERGENCY EXPENSE NAVIGATOR (Idea 08)
  // -------------------------------------------------------------------------
  async renderEmergencyNavigator() {
    const container = document.getElementById("emergency-content-container");
    if (!container) return;

    const laptops = await window.api.getProducts({ category: "laptop" });
    const thinkpad = laptops.find(l => l.id === "laptop-lenovo-t14s");
    const acer = laptops.find(l => l.id === "laptop-acer-aspire5");

    container.innerHTML = `
      <div class="emergency-navigator-box">
        <div class="emergency-alert-header">
          <div class="emer-icon">🚨</div>
          <div>
            <h2>Emergency Expense & Urgent Replacement Navigator</h2>
            <p>Comparing high-durability options with fast delivery and verified warranty coverage under $500 budget.</p>
          </div>
        </div>

        <div class="emergency-tradeoff-summary">
          <div class="summary-pill highlight">
            <strong>Key Trade-Off Decision:</strong> ThinkPad T14s ($499.00) vs Acer Aspire 5 ($389.00).
            ThinkPad offers <strong>1-Day Express Dispatch</strong> and MIL-SPEC military-grade durability, staying $1.00 under your $500 budget. Acer saves $111.00 but ships in 2 days.
          </div>
        </div>

        <div class="emergency-cards-grid">
          ${thinkpad ? `
            <div class="emergency-card card recommended-emer">
              <div class="emer-badge">⚡ Recommended for Urgent Work</div>
              <h3>${thinkpad.name}</h3>
              <p class="emer-brand">Brand: ${thinkpad.brand} • Certified Grade-A Refurbished</p>
              <div class="emer-price-row">
                <span class="price-val">$${thinkpad.price.toFixed(2)}</span>
                <span class="badge badge-success">$1.00 Under $500 Budget</span>
              </div>
              <ul class="emer-perks">
                <li>🚀 <strong>1-Day Express Delivery:</strong> Arrives tomorrow</li>
                <li>🛡️ <strong>12-Month Hardware Warranty:</strong> Full replacement protection</li>
                <li>⭐ <strong>Reliability Rating:</strong> 9.6 / 10 (MIL-SPEC spill-resistant chassis)</li>
                <li>🔋 <strong>Battery:</strong> 14.0 hours with RapidCharge</li>
              </ul>
              <div class="emer-action">
                <button class="btn btn-success btn-block" onclick="app.selectEmergencyProduct('${thinkpad.id}')">
                  Select ThinkPad T14s & Proceed to Checkout ➔
                </button>
              </div>
            </div>
          ` : ''}

          ${acer ? `
            <div class="emergency-card card">
              <div class="emer-badge badge-neutral">Budget-Saver Alternative</div>
              <h3>${acer.name}</h3>
              <p class="emer-brand">Brand: ${acer.brand} • Brand New Retail</p>
              <div class="emer-price-row">
                <span class="price-val">$${acer.price.toFixed(2)}</span>
                <span class="badge badge-info">Saves $111.00</span>
              </div>
              <ul class="emer-perks">
                <li>⏱️ <strong>2-Day Delivery:</strong> Standard shipping</li>
                <li>🛡️ <strong>12-Month Warranty:</strong> Manufacturer limited warranty</li>
                <li>⭐ <strong>Reliability Rating:</strong> 8.6 / 10</li>
                <li>🔋 <strong>Battery:</strong> 8.5 hours</li>
              </ul>
              <div class="emer-action">
                <button class="btn btn-outline btn-block" onclick="app.selectEmergencyProduct('${acer.id}')">
                  Select Acer Aspire 5 & Proceed to Checkout ➔
                </button>
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  selectEmergencyProduct(productId) {
    if (window.budgetGuardUI) {
      window.budgetGuardUI.statedBudget = 500.00;
      window.budgetGuardUI.selectedItemIds = [productId];
      window.budgetGuardUI.recalculateCurrentBundle();
    }
    if (window.paypalCheckoutUI) {
      window.paypalCheckoutUI.initiateCheckout();
    }
  }

  openBillsModal() {
    const modal = document.getElementById("bills-modal");
    if (modal) {
      modal.classList.remove("hidden");
      if (window.billManagerUI) window.billManagerUI.refreshBills();
    }
  }

  // -------------------------------------------------------------------------
  // 6. SETUP EVENT LISTENERS
  // -------------------------------------------------------------------------
  setupEventListeners() {
    // Nav buttons
    document.getElementById("nav-btn-dorm")?.addEventListener("click", () => this.switchView("dorm"));
    document.getElementById("nav-btn-emergency")?.addEventListener("click", () => this.switchView("emergency"));
    document.getElementById("nav-btn-catalogue")?.addEventListener("click", () => this.switchView("catalogue"));
    document.getElementById("nav-btn-comparison")?.addEventListener("click", () => this.switchView("comparison"));

    // Quick fill chips
    document.getElementById("chip-demo-dorm")?.addEventListener("click", () => this.loadDormScenario());
    document.getElementById("chip-demo-emergency")?.addEventListener("click", () => this.loadEmergencyScenario());

    // Stated budget change
    document.getElementById("stated-budget-input")?.addEventListener("change", (e) => {
      if (window.budgetGuardUI) window.budgetGuardUI.setStatedBudget(e.target.value);
    });

    // Form submit / Analyze button
    document.getElementById("shopping-input-form")?.addEventListener("submit", (e) => {
      e.preventDefault();
      const budgetVal = document.getElementById("stated-budget-input")?.value || 150.00;
      if (window.budgetGuardUI) {
        window.budgetGuardUI.statedBudget = parseFloat(budgetVal);
        window.budgetGuardUI.runOptimization(CONFIG.DEFAULT_DORM_CATEGORIES, "reliability");
      }
    });

    // Checkout modal triggers
    document.getElementById("btn-proceed-checkout")?.addEventListener("click", () => {
      if (window.paypalCheckoutUI) window.paypalCheckoutUI.initiateCheckout();
    });

    // Accessibility buttons
    document.getElementById("btn-high-contrast")?.addEventListener("click", () => {
      if (window.a11y) window.a11y.toggleHighContrast();
    });
    document.getElementById("btn-text-scale")?.addEventListener("click", () => {
      if (window.a11y) window.a11y.cycleTextScale();
    });
    document.getElementById("btn-tts")?.addEventListener("click", () => {
      if (window.a11y) {
        if (window.a11y.isSpeaking) window.a11y.stopSpeaking();
        else window.a11y.readCurrentSummary();
      }
    });
    document.getElementById("btn-voice-mic")?.addEventListener("click", () => {
      if (window.voice) window.voice.toggleListening();
    });
    document.getElementById("btn-open-bills")?.addEventListener("click", () => {
      this.openBillsModal();
    });
    document.getElementById("btn-close-bills")?.addEventListener("click", () => {
      document.getElementById("bills-modal")?.classList.add("hidden");
    });
    document.getElementById("btn-close-shortcuts")?.addEventListener("click", () => {
      document.getElementById("shortcuts-modal")?.classList.add("hidden");
    });
    document.getElementById("btn-close-price-history")?.addEventListener("click", () => {
      document.getElementById("price-history-modal")?.classList.add("hidden");
    });
    document.getElementById("btn-close-checkout")?.addEventListener("click", () => {
      if (window.paypalCheckoutUI) window.paypalCheckoutUI.closeCheckoutModal();
    });

    // Add bill form
    document.getElementById("add-bill-form")?.addEventListener("submit", (e) => {
      if (window.billManagerUI) window.billManagerUI.handleAddBill(e);
    });

    // Catalogue filters
    document.getElementById("cat-filter-select")?.addEventListener("change", (e) => {
      this.activeCategoryFilter = e.target.value;
      this.renderCatalogueCards();
    });
    document.getElementById("cat-sort-select")?.addEventListener("change", (e) => {
      this.activeSort = e.target.value;
      this.renderCatalogueCards();
    });
    document.getElementById("cat-search-input")?.addEventListener("input", (e) => {
      this.searchTerm = e.target.value;
      this.renderCatalogueCards();
    });
  }

  updateConnectionStatusBadge(isOnline, message) {
    const badge = document.getElementById("backend-status-badge");
    if (!badge) return;

    if (isOnline) {
      badge.className = "status-badge badge-online";
      badge.innerHTML = `<span class="dot"></span> <span>Backend: Online (${CONFIG.API_BASE_URL})</span>`;
      badge.title = message;
    } else {
      badge.className = "status-badge badge-offline";
      badge.innerHTML = `<span class="dot"></span> <span>Local Mode (Backend: Offline)</span>`;
      badge.title = message;
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

// Global instance
const app = new PayPilotApp();
if (typeof window !== "undefined") {
  window.app = app;
  window.addEventListener("DOMContentLoaded", () => app.init());
}

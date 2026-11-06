/**
 * PayPilot AI — Proactive Financial Health & Bill Manager UI
 * Module: Suryansh (Bill Awareness Integration)
 *
 * Implements:
 * 1. User-recorded bill listing with 7-day proximity filter
 * 2. Visual comparison of planned shopping budget vs 7-day upcoming bills
 * 3. Safe disposable shopping budget calculation
 * 4. Add/delete bill records
 * 5. Transparent disclaimer ensuring no false claims of bank balance access
 */

class BillManagerUI {
  constructor(apiClient = window.api) {
    this.api = apiClient;
    this.bills = [];
    this.upcomingTotal = 0;
  }

  async init() {
    await this.refreshBills();
  }

  async refreshBills() {
    this.bills = await this.api.getBills();
    this.renderBillsList();
    this.updateBudgetCardCallout();
  }


async updateBudgetCardCallout(statedBudget = 150.00) {
    const summary = await this.api.getBillsSummary(statedBudget, 7);

    const safeSummary = summary || {};

    const upcomingTotal = Number(
        safeSummary.upcoming_bills_total ?? 0
    );

    const disposableBudget = Number(
        safeSummary.disposable_budget ?? 0
    );

    const safeUpcomingTotal = Number.isFinite(upcomingTotal)
        ? upcomingTotal
        : 0;

    const safeDisposableBudget = Number.isFinite(disposableBudget)
        ? disposableBudget
        : 0;

    this.upcomingTotal = safeUpcomingTotal;

    const calloutEl = document.getElementById("bills-budget-callout");

    if (calloutEl) {
        calloutEl.innerHTML = `
            <div class="bill-summary-chip ${safeDisposableBudget >= 0 ? 'safe' : 'danger'}">
                <div class="chip-row">
                    <span class="chip-label">📅 7-Day Bills Total:</span>
                    <strong class="chip-val">$${safeUpcomingTotal.toFixed(2)}</strong>
                </div>

                <div class="chip-row">
                    <span class="chip-label">💡 Safe Disposable Balance:</span>
                    <strong class="chip-val ${safeDisposableBudget >= 0 ? 'text-green' : 'text-red'}">
                        $${safeDisposableBudget.toFixed(2)}
                    </strong>
                </div>

                <p class="chip-disclaimer">
                    <small>ℹ️ ${safeSummary.disclaimer || "Estimated financial summary."}</small>
                </p>
            </div>
        `;
    }
}

  renderBillsList() {
    const container = document.getElementById("bills-list-container");
    if (!container) return;

    if (!this.bills || this.bills.length === 0) {
      container.innerHTML = `<p class="empty-state">No bills recorded yet.</p>`;
      return;
    }

    const ref = new Date(CONFIG.REFERENCE_DATE);

    container.innerHTML = this.bills.map(bill => {
      const dueDate = new Date(bill.due_date);
      const diffDays = Math.ceil((dueDate - ref) / (1000 * 60 * 60 * 24));
      const isUrgent = diffDays >= 0 && diffDays <= 7;
      const isPast = diffDays < 0;

      let badgeClass = "badge-neutral";
      let badgeText = `Due in ${diffDays} days`;
      if (isUrgent) {
        badgeClass = "badge-warning";
        badgeText = `⚠️ Due in ${diffDays} day${diffDays === 1 ? '' : 's'} (This Week)`;
      } else if (isPast) {
        badgeClass = "badge-danger";
        badgeText = `Overdue`;
      }

      return `
        <div class="bill-card ${isUrgent ? 'urgent-bill' : ''}">
          <div class="bill-header">
            <div>
              <h4 class="bill-title">${this.escapeHtml(bill.title)}</h4>
              <span class="bill-category">${this.escapeHtml(bill.category)}</span>
            </div>
            <div class="bill-amount-box">
              <span class="bill-amount">$${parseFloat(bill.amount).toFixed(2)}</span>
            </div>
          </div>
          <div class="bill-footer">
            <span class="bill-badge ${badgeClass}">${badgeText}</span>
            <span class="bill-due-date">Due: ${bill.due_date}</span>
          </div>
        </div>
      `;
    }).join("");
  }

  async handleAddBill(e) {
    e.preventDefault();
    const titleInput = document.getElementById("new-bill-title");
    const amountInput = document.getElementById("new-bill-amount");
    const dateInput = document.getElementById("new-bill-date");
    const categoryInput = document.getElementById("new-bill-category");

    if (!titleInput.value || !amountInput.value || !dateInput.value) {
      alert("Please fill in title, amount, and due date.");
      return;
    }

    const billData = {
      title: titleInput.value.trim(),
      amount: parseFloat(amountInput.value),
      due_date: dateInput.value,
      category: categoryInput ? categoryInput.value : "General",
      is_recurring: true
    };

    await this.api.addBill(billData);
    titleInput.value = "";
    amountInput.value = "";

    await this.refreshBills();
    if (window.a11y) {
      window.a11y.announce(`Added bill ${billData.title} for $${billData.amount.toFixed(2)}`, "polite");
    }
  }

  escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
}

// Global instance
const billManagerUI = new BillManagerUI();
if (typeof window !== "undefined") {
  window.billManagerUI = billManagerUI;
}

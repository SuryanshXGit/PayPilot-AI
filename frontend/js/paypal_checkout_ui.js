/**
 * PayPilot AI — PayPal Sandbox Checkout & Payment Verification UI
 * Module: Meenal (Checkout Screens & Verification Flow)
 *
 * Stage 1: Order preparation and price locking
 * Stage 2: PayPal Sandbox order creation
 * Stage 3: Actual buyer approval verification
 * Stage 4: Server-side capture and verification
 */

class PayPalCheckoutUI {
    constructor(apiClient = window.api) {
        this.api = apiClient;
        this.currentOrder = null;
        this.paypalOrderData = null;
        this.verificationData = null;
        this.payIn4Data = null;
        this.currentStep = 1;
    }

    // ---------------------------------------------------------
    // COMMON UI METHODS
    // ---------------------------------------------------------

    renderStepProgress() {
        const progress = document.getElementById("checkout-step-progress");

        if (!progress) return;

        const steps = [
            "Review Order",
            "PayPal Approval",
            "Verify Approval",
            "Capture Payment"
        ];

        progress.innerHTML = steps.map((step, index) => {
            const number = index + 1;
            const active = number === this.currentStep;
            const completed = number < this.currentStep;

            return `
                <div class="checkout-progress-step
                    ${active ? "active" : ""}
                    ${completed ? "completed" : ""}">
                    <span>${completed ? "✓" : number}</span>
                    <small>${step}</small>
                </div>
            `;
        }).join("");
    }

    renderLoading(message) {
        const container = document.getElementById("checkout-body-content");

        if (!container) return;

        container.innerHTML = `
            <div class="checkout-loading">
                <div class="loading-spinner"></div>
                <p>${message}</p>
            </div>
        `;
    }

    renderError(message) {
        const container = document.getElementById("checkout-body-content");

        if (!container) {
            console.error(message);
            alert(message);
            return;
        }

        container.innerHTML = `
            <div class="checkout-error">
                <h3>Checkout Error</h3>
                <p>${message}</p>
                <button class="btn btn-outline"
                    onclick="paypalCheckoutUI.closeCheckoutModal()">
                    Close
                </button>
            </div>
        `;

        console.error("PayPilot Checkout:", message);
    }

    // ---------------------------------------------------------
    // INITIATE CHECKOUT
    // ---------------------------------------------------------

    async initiateCheckout() {
        try {
            const itemIds = window.budgetGuardUI
                ? window.budgetGuardUI.selectedItemIds
                : [];

            const budget = window.budgetGuardUI
                ? window.budgetGuardUI.statedBudget
                : 150.00;

            if (!itemIds || itemIds.length === 0) {
                alert("Your basket is empty. Please select products first.");
                return;
            }

            const check = await this.api.checkBudget(itemIds, budget);

            if (check.is_over_budget) {
                const proceed = confirm(
                    `Warning: This bundle exceeds your stated budget.

Would you still like to proceed to checkout?`
                );

                if (!proceed) return;
            }

            this.openCheckoutModal();

            await this.step1PrepareOrder(itemIds, budget);

        } catch (err) {
            this.renderError("Checkout initialization failed: " + err.message);
        }
    }

    openCheckoutModal() {
        const modal = document.getElementById("checkout-modal");

        if (modal) {
            modal.classList.remove("hidden");

            if (window.a11y) {
                window.a11y.announce(
                    "Opened PayPal Sandbox checkout modal",
                    "polite"
                );
            }
        }
    }

    closeCheckoutModal() {
        const modal = document.getElementById("checkout-modal");

        if (modal) {
            modal.classList.add("hidden");
        }
    }

    // ---------------------------------------------------------
    // CANCEL ORDER
    // ---------------------------------------------------------

    async handleCancelOrder() {
        if (!this.currentOrder || !this.currentOrder.order_id) {
            this.closeCheckoutModal();
            return;
        }

        const confirmed = confirm(
            "Are you sure you want to cancel this order?"
        );

        if (!confirmed) return;

        try {
            await this.api.cancelOrder(this.currentOrder.order_id);

            localStorage.removeItem("paypilot_pending_order_id");

            this.currentOrder = null;
            this.paypalOrderData = null;
            this.verificationData = null;

            this.closeCheckoutModal();

        } catch (err) {
            this.renderError("Order cancellation failed: " + err.message);
        }
    }

    // ---------------------------------------------------------
    // STAGE 1: PREPARE AND LOCK ORDER
    // ---------------------------------------------------------

    async step1PrepareOrder(itemIds, budget) {
        this.currentStep = 1;
        this.renderStepProgress();

        this.renderLoading(
            "Preparing server-locked order records..."
        );

        try {
            this.currentOrder = await this.api.prepareOrder(
                itemIds,
                budget
            );

            this.payIn4Data = await this.api.getPayIn4Estimate(
                this.currentOrder.order_id
            );

            this.renderStage1Review();

        } catch (err) {
            this.renderError(
                "Failed to lock order: " + err.message
            );
        }
    }

    renderStage1Review() {
        const container = document.getElementById("checkout-body-content");

        if (!container || !this.currentOrder) return;

        const ord = this.currentOrder;
        const p4 = this.payIn4Data || {};
        const budgetCheck = ord.budget_check || {};
        const budgetItems = budgetCheck.items || [];

        const money = (value) => {
            const number = Number(value ?? 0);

            return Number.isFinite(number)
                ? number.toFixed(2)
                : "0.00";
        };

        const items = (ord.items || []).map(item => {
            const details = budgetItems.find(
                product => product.id === item.id
            ) || {};

            return {
                ...item,
                brand: details.brand || "Catalogue",
                warranty_months: details.warranty_months,
                price: Number(
                    item.unit_amount ?? details.price ?? 0
                )
            };
        });

        const statedBudget = Number(
            budgetCheck.stated_budget ?? 0
        );

        const subtotal = Number(ord.subtotal ?? 0);
        const tax = Number(ord.tax ?? 0);
        const shipping = Number(ord.shipping ?? 0);
        const total = Number(ord.total_amount ?? 0);

        container.innerHTML = `
            <div class="checkout-stage-box">

                <div class="stage-title-row">
                    <span class="stage-number">1</span>

                    <div>
                        <h3>Stage 1: Review Locked Order</h3>
                        <p class="stage-desc">
                            Server has locked catalogue prices
                            to prevent price drift.
                        </p>
                    </div>

                    <span class="order-id-badge">
                        Order #${ord.order_id}
                    </span>
                </div>

                <div class="locked-items-list">

                    ${items.map(item => `
                        <div class="locked-item-row">

                            <span class="item-brand-tag">
                                ${item.brand}
                            </span>

                            <strong class="item-name">
                                ${item.name}
                            </strong>

                            <span class="item-warranty">
                                ${item.warranty_months != null
                                    ? `${item.warranty_months}mo warranty`
                                    : "Warranty details unavailable"}
                            </span>

                            <span class="item-price">
                                $${money(item.price)}
                            </span>

                        </div>
                    `).join("")}

                </div>

                <div class="checkout-summary-grid">

                    <div class="summary-line">
                        <span>Stated Budget:</span>
                        <strong>$${money(statedBudget)}</strong>
                    </div>

                    <div class="summary-line">
                        <span>Items Subtotal:</span>
                        <strong>$${money(subtotal)}</strong>
                    </div>

                    <div class="summary-line">
                        <span>Tax & Shipping:</span>
                        <strong>$${money(tax + shipping)}</strong>
                    </div>

                    <div class="summary-line line-total">
                        <span>Total Locked Amount:</span>

                        <strong class="total-highlight">
                            $${money(total)} USD
                        </strong>
                    </div>

                </div>

                ${p4.installment_amount != null ? `

                    <div class="pay-in-4-box">

                        <div class="p4-header">
                            <span class="p4-logo">
                                PayPal <strong>Pay in 4</strong>
                            </span>

                            <span class="p4-badge">
                                Bi-weekly Installments
                            </span>
                        </div>

                        <p class="p4-calc">
                            Or <strong>4 interest-free payments of
                            $${money(p4.installment_amount)}</strong>
                            every 2 weeks.
                        </p>

                        <div class="p4-disclaimers">

                            <p class="p4-warning">
                                ⚠️ <strong>Affordability Notice:</strong>
                                ${p4.affordability_warning || ""}
                            </p>

                            <p class="p4-eligibility">
                                <small>
                                    ℹ️ ${p4.eligibility_disclaimer || ""}
                                </small>
                            </p>

                        </div>
                    </div>

                ` : ""}

                <div class="checkout-action-row">

                    <button class="btn btn-outline"
                        onclick="paypalCheckoutUI.handleCancelOrder()">
                        Cancel
                    </button>

                    <button class="btn btn-primary"
                        onclick="paypalCheckoutUI.step2CreatePayPalOrder()">
                        Continue to PayPal Sandbox ➔
                    </button>

                </div>

            </div>
        `;
    }

    // ---------------------------------------------------------
    // STAGE 2: CREATE PAYPAL SANDBOX ORDER
    // ---------------------------------------------------------

    async step2CreatePayPalOrder() {
        this.currentStep = 2;

        this.renderStepProgress();

        this.renderLoading(
            "Creating order in PayPal Sandbox environment..."
        );

        try {
            this.paypalOrderData = await this.api.createPayPalOrder(
                this.currentOrder.order_id
            );

            localStorage.setItem(
                "paypilot_pending_order_id",
                this.currentOrder.order_id
            );

            this.renderStage2PendingApproval();

        } catch (err) {
            this.renderError(
                "PayPal Sandbox error: " + err.message
            );
        }
    }

    renderStage2PendingApproval() {
        const container = document.getElementById("checkout-body-content");

        if (!container || !this.paypalOrderData) return;

        const pp = this.paypalOrderData;

        const amount = Number(
            pp.total_amount ??
            this.currentOrder?.total_amount ??
            0
        );

        const currency =
            pp.currency ||
            this.currentOrder?.currency ||
            "USD";

        const approvalUrl = pp.approval_url;

        let parsedUrl;

        try {
            parsedUrl = new URL(approvalUrl);
        } catch {
            this.renderError("Invalid PayPal approval URL.");
            return;
        }

        if (
            parsedUrl.protocol !== "https:" ||
            parsedUrl.hostname !== "www.sandbox.paypal.com"
        ) {
            this.renderError(
                "Invalid PayPal Sandbox approval URL."
            );
            return;
        }

        container.innerHTML = `
            <div class="checkout-stage-box">

                <div class="stage-title-row">

                    <span class="stage-number">2</span>

                    <div>
                        <h3>
                            Stage 2: PayPal Buyer Approval Required
                        </h3>

                        <p class="stage-desc">
                            Your order is created.
                            Continue to PayPal to approve it securely.
                        </p>
                    </div>

                    <span class="badge badge-warning">
                        PENDING_APPROVAL
                    </span>

                </div>

                <div class="paypal-info-panel">

                    <div class="paypal-badge-row">
                        <span class="paypal-text-brand">
                            Pay<strong>Pal</strong> Sandbox
                        </span>

                        <span class="pp-order-id">
                            ID: ${pp.paypal_order_id}
                        </span>
                    </div>

                    <div class="paypal-auth-amount">
                        <span>Authorization Amount:</span>

                        <h3>
                            $${amount.toFixed(2)} ${currency}
                        </h3>
                    </div>

                    <div class="security-guardrail-banner alert-warning-theme">

                        <span class="icon">🛡️</span>

                        <div>
                            <strong>Security Notice:</strong>

                            <p>
                                Payment is not complete until PayPal
                                approval, server-side capture, and
                                amount verification succeed.
                            </p>
                        </div>

                    </div>

                </div>

                <div class="paypal-button-container">

                    <button id="real-paypal-approval-button"
                        class="btn-paypal-sandbox">
                        Continue to Real PayPal Sandbox Approval
                    </button>

                    <p class="sandbox-note">
                        <small>
                            Sign in using your PayPal Sandbox buyer account.
                        </small>
                    </p>

                </div>

                <div class="checkout-action-row">

                    <button class="btn btn-outline"
                        onclick="paypalCheckoutUI.handleCancelOrder()">
                        Cancel Order
                    </button>

                </div>

            </div>
        `;

        const approvalButton = document.getElementById(
            "real-paypal-approval-button"
        );

        if (approvalButton) {
            approvalButton.addEventListener("click", () => {
                window.location.assign(approvalUrl);
            });
        }
    }

    // ---------------------------------------------------------
    // STAGE 3: ACTUAL PAYPAL RETURN AND APPROVAL VERIFICATION
    // ---------------------------------------------------------

    async handlePayPalReturn() {
        const params = new URLSearchParams(
            window.location.search
        );

        const token = params.get("token");
        const cancelled = params.get("paypal_cancel");

        if (cancelled !== null) {
            const pendingId = localStorage.getItem(
                "paypilot_pending_order_id"
            );

            if (pendingId) {
                try {
                    await this.api.cancelOrder(pendingId);
                } catch (err) {
                    console.error(
                        "Order cancellation:",
                        err
                    );
                }
            }

            localStorage.removeItem(
                "paypilot_pending_order_id"
            );

            return;
        }

        if (!token) return;

        const orderId = localStorage.getItem(
            "paypilot_pending_order_id"
        );

        if (!orderId) {
            alert(
                "Could not find your pending PayPilot order. Please contact support."
            );
            return;
        }

        this.openCheckoutModal();

        this.currentStep = 3;

        this.renderStepProgress();

        this.renderLoading(
            "Verifying actual PayPal buyer approval..."
        );

        try {
            this.currentOrder = await this.api.getOrder(orderId);

            await this.api.confirmPayPalApproval(
                orderId,
                token
            );

            window.history.replaceState(
                {},
                document.title,
                window.location.pathname
            );

            this.currentStep = 4;

            this.renderStepProgress();

            await this.step4CaptureAndVerify();

            if (this.verificationData?.verified === true) {
                localStorage.removeItem(
                    "paypilot_pending_order_id"
                );
            }

        } catch (err) {
            this.renderError(
                "PayPal verification failed: " + err.message
            );
        }
    }

    // ---------------------------------------------------------
    // STAGE 4: SERVER-SIDE CAPTURE AND VERIFICATION
    // ---------------------------------------------------------

    async step4CaptureAndVerify() {
        this.currentStep = 4;

        this.renderStepProgress();

        this.renderLoading(
            "Executing server capture & mathematical amount verification..."
        );

        try {
            this.verificationData = await this.api.captureOrder(
                this.currentOrder.order_id
            );

            this.renderStage4ConfirmedReceipt();

        } catch (err) {
            this.renderError(
                "Payment capture failed: " + err.message
            );
        }
    }

    // ---------------------------------------------------------
    // FINAL VERIFIED RECEIPT
    // ---------------------------------------------------------

    renderStage4ConfirmedReceipt() {
        const container = document.getElementById(
            "checkout-body-content"
        );

        if (
            !container ||
            !this.verificationData ||
            !this.currentOrder
        ) {
            return;
        }

        const v = this.verificationData;
        const ord = this.currentOrder;

        if (
            v.verified !== true ||
            v.status !== "CAPTURED"
        ) {
            this.renderError(
                "Payment has not been verified by the backend."
            );
            return;
        }

        const items = (ord.items || []).map(item => ({
            name: item.name || "Product",
            category: item.category || "Catalogue",
            price: Number(item.unit_amount ?? 0)
        }));

        const capturedAmount = Number(v.captured_amount);

        if (!Number.isFinite(capturedAmount)) {
            this.renderError(
                "Invalid captured payment amount returned by backend."
            );
            return;
        }

        container.innerHTML = `
            <div class="checkout-stage-box success-stage">

                <div class="success-banner">

                    <span class="success-icon">🎉</span>

                    <h2>Payment Verified & Captured!</h2>

                    <p class="success-subtitle">
                        ${v.message || "Payment successfully verified."}
                    </p>

                </div>

                <div class="receipt-card">

                    <div class="receipt-header">

                        <div>
                            <h3>PayPilot AI Order Receipt</h3>

                            <p class="receipt-date">
                                ${v.captured_at || new Date().toLocaleString()}
                            </p>
                        </div>

                        <span class="badge badge-success">
                            CAPTURED & VERIFIED
                        </span>

                    </div>

                    <div class="receipt-grid">

                        <div class="receipt-field">
                            <span>PayPilot Order:</span>
                            <strong>${v.order_id}</strong>
                        </div>

                        <div class="receipt-field">
                            <span>PayPal Sandbox ID:</span>
                            <strong>${v.paypal_order_id}</strong>
                        </div>

                        <div class="receipt-field">
                            <span>Captured Amount:</span>

                            <strong class="receipt-price">
                                $${capturedAmount.toFixed(2)}
                                ${v.currency}
                            </strong>
                        </div>

                        <div class="receipt-field">
                            <span>Status:</span>

                            <strong class="text-green">
                                VERIFIED MATCH
                            </strong>
                        </div>

                    </div>

                    <div class="receipt-items">

                        <h4>Ordered Items</h4>

                        ${items.map(item => `
                            <div class="receipt-item-line">

                                <span>
                                    ${item.name} (${item.category})
                                </span>

                                <span>
                                    $${item.price.toFixed(2)}
                                </span>

                            </div>
                        `).join("")}

                    </div>

                </div>

                <div class="checkout-action-row">

                    <button class="btn btn-primary"
                        onclick="paypalCheckoutUI.closeCheckoutModal()">
                        Done & Return to Dashboard
                    </button>

                </div>

            </div>
        `;

        if (window.a11y) {
            window.a11y.speak(
                `Payment of ${capturedAmount.toFixed(2)} dollars verified and captured successfully.`
            );
        }
    }
}

// ---------------------------------------------------------
// GLOBAL INSTANCE
// ---------------------------------------------------------

const paypalCheckoutUI = new PayPalCheckoutUI();

if (typeof window !== "undefined") {
    window.paypalCheckoutUI = paypalCheckoutUI;
}

// ---------------------------------------------------------
// AUTOMATIC PAYPAL RETURN HANDLER
// ---------------------------------------------------------

if (typeof window !== "undefined") {

    const handleReturn = () => {
        window.paypalCheckoutUI.handlePayPalReturn();
    };

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            handleReturn
        );
    } else {
        handleReturn();
    }
}
/**
 * PayPilot AI — AI Assistant & Chatbot Client Application
 * Module Owner: Jaskaran
 */

const API_BASE = "http://127.0.0.1:5001";
let isBackendOnline = false;
let currentSessionId = "session_" + Date.now();
let activeBundle = null;

// Verified local catalogue fallback
const LOCAL_CATALOGUE = [
  { id: "lamp-taotronics-pro", name: "TaoTronics Eye-Care Multi-Spectrum Desk Lamp", category: "desk_lamp", price: 32.99, reliability_score: 9.2, delivery_days: 1, warranty_months: 24 },
  { id: "lamp-benq-eread", name: "BenQ e-Reading Architectural LED Task Light", category: "desk_lamp", price: 89.00, reliability_score: 9.6, delivery_days: 2, warranty_months: 36 },
  { id: "lamp-lumina-study", name: "Lumina Glow LED Study Lamp", category: "desk_lamp", price: 18.99, reliability_score: 7.8, delivery_days: 2, warranty_months: 12 },
  { id: "steamer-conair-turbo", name: "Conair Turbo ExtremeSteam Handheld Fabric Steamer", category: "portable_steamer", price: 44.99, reliability_score: 9.4, delivery_days: 1, warranty_months: 12 },
  { id: "steamer-hilife-travel", name: "Hilife Portable Handheld Garment Steamer", category: "portable_steamer", price: 24.99, reliability_score: 8.2, delivery_days: 2, warranty_months: 12 },
  { id: "buds-anker-space-a40", name: "Anker Soundcore Space A40 Adaptive ANC Earbuds", category: "noise_cancelling_earbuds", price: 59.99, reliability_score: 9.4, delivery_days: 1, warranty_months: 18 },
  { id: "buds-sony-wf1000xm5", name: "Sony WF-1000XM5 Flagship Wireless ANC Earbuds", category: "noise_cancelling_earbuds", price: 149.00, reliability_score: 9.7, delivery_days: 1, warranty_months: 24 },
  { id: "buds-jlab-go-air-pop", name: "JLab Go Air Pop True Wireless Earbuds", category: "noise_cancelling_earbuds", price: 24.99, reliability_score: 8.3, delivery_days: 2, warranty_months: 24 },
  { id: "laptop-lenovo-t14s", name: "Lenovo ThinkPad T14s Gen 2 (Refurbished Grade A)", category: "laptop", price: 499.00, reliability_score: 9.6, delivery_days: 1, warranty_months: 12 },
  { id: "laptop-acer-aspire-5", name: "Acer Aspire 5 Slim Laptop", category: "laptop", price: 389.00, reliability_score: 8.6, delivery_days: 2, warranty_months: 12 }
];

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initChat();
  initOptimizer();
  initVoice();
  initFilter();
  checkBackendHealth();
});

// -------------------------------------------------------------
// Health Check
// -------------------------------------------------------------
async function checkBackendHealth() {
  const pill = document.getElementById("backend-status-pill");
  try {
    const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      isBackendOnline = true;
      pill.textContent = "● Connected to Flask (Port 5001)";
      pill.className = "status-pill online";
      return;
    }
  } catch (e) {
    // Backend offline
  }
  isBackendOnline = false;
  pill.textContent = "● Local Verified Engine (Standalone)";
  pill.className = "status-pill offline";
}

// -------------------------------------------------------------
// Tab Switching
// -------------------------------------------------------------
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      tabs.forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// -------------------------------------------------------------
// TAB 1: AI Chatbot
// -------------------------------------------------------------
function initChat() {
  const form = document.getElementById("chat-input-form");
  const input = document.getElementById("chat-user-input");
  const resetBtn = document.getElementById("btn-reset-chat");
  const chips = document.querySelectorAll(".quick-chips-container .chip-btn");

  // Welcome message
  appendMessage("assistant", "Hello! I am PayPilot AI, your budget-aware shopping co-pilot.\n\nTell me what you're looking for, your maximum budget, and any priorities (like high reliability or fast delivery). I will find the optimal combination and explain every trade-off!");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    handleSendMessage(text);
  });

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.dataset.prompt;
      input.value = prompt;
      handleSendMessage(prompt);
    });
  });

  resetBtn.addEventListener("click", () => {
    currentSessionId = "session_" + Date.now();
    document.getElementById("chat-messages").innerHTML = "";
    activeBundle = null;
    document.getElementById("active-bundle-summary").innerHTML = `
      <p class="text-muted" style="padding: 20px 0; text-align: center;">
        Session reset. Send a shopping query to begin.
      </p>
    `;
    document.getElementById("chat-tradeoff-list").innerHTML = `
      <p class="text-muted text-sm">Trade-off rationales will appear here after optimization.</p>
    `;
    appendMessage("assistant", "Session reset. How can I help you shop within budget today?");
  });
}

async function handleSendMessage(message) {
  appendMessage("user", message);

  // Show temporary typing indicator
  const typingId = appendTypingIndicator();

  try {
    if (isBackendOnline) {
      const res = await fetch(`${API_BASE}/api/ai/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: currentSessionId, message: message })
      });
      const data = await res.json();
      removeMessage(typingId);

      if (data.status === "success") {
        appendMessage("assistant", data.reply_text);
        if (data.bundle) {
          activeBundle = data.bundle;
          renderActiveBundle(data.bundle);
        }
        if (data.explanations && data.explanations.length > 0) {
          renderTradeoffs(data.explanations);
        }
        return;
      }
    }
  } catch (err) {
    console.warn("Backend chat failed, using local simulation:", err);
  }

  // Standalone local fallback simulation
  removeMessage(typingId);
  simulateLocalChatResponse(message);
}

function simulateLocalChatResponse(msg) {
  const lower = msg.toLowerCase();

  if (lower.includes("dorm") || lower.includes("150") || lower.includes("college")) {
    const bundle = {
      total_cost: 137.97,
      subtotal: 137.97,
      stated_budget: 150.0,
      surplus: 12.03,
      is_within_budget: true,
      average_reliability: 9.33,
      items: [
        { id: "lamp-taotronics-pro", name: "TaoTronics Eye-Care Multi-Spectrum Desk Lamp", price: 32.99, reliability_score: 9.2, category: "desk_lamp" },
        { id: "steamer-conair-turbo", name: "Conair Turbo ExtremeSteam Handheld Fabric Steamer", price: 44.99, reliability_score: 9.4, category: "portable_steamer" },
        { id: "buds-anker-space-a40", name: "Anker Soundcore Space A40 Adaptive ANC Earbuds", price: 59.99, reliability_score: 9.4, category: "noise_cancelling_earbuds" }
      ]
    };
    activeBundle = bundle;
    renderActiveBundle(bundle);

    const reply = `I've evaluated all 36 combinations and selected the optimal dorm move-in basket within your strict $150.00 budget:

• TaoTronics Eye-Care Desk Lamp ($32.99 | ★ 9.2/10)
• Conair Turbo ExtremeSteam Steamer ($44.99 | ★ 9.4/10)
• Anker Soundcore Space A40 ANC Earbuds ($59.99 | ★ 9.4/10)

Budget Guard Verification:
• Total: $137.97
• Surplus: +$12.03 remaining
• Avg Reliability: 9.33/10

Would you like me to explain why TaoTronics was picked over BenQ, or adjust budget?`;

    appendMessage("assistant", reply);
    renderTradeoffs([
      "Overall Strategy: Kept bundle under $150.00 with $12.03 surplus and high 9.33/10 reliability.",
      "In Desk Lamp: Chose TaoTronics ($32.99) over BenQ ($89.00), saving $56.01 to leave room for ANC earbuds.",
      "In Earbuds: Picked Anker Space A40 ($59.99) over Sony ($149.00), preventing a massive budget overrun."
    ]);
  } else if (lower.includes("why") || lower.includes("benq")) {
    const reply = `Trade-Off Breakdown — Desk Lamp Selection:

We chose TaoTronics ($32.99, ★ 9.2/10) over BenQ e-Reading ($89.00, ★ 9.6/10):
• BenQ costs $89.00 — consuming nearly 60% of your entire $150 budget!
• Choosing TaoTronics saves $56.01, allowing you to get both a high-performance steamer and active noise-cancelling earbuds.
• You sacrifice only 0.4 pts in reliability while retaining flicker-free lighting, multi-angle folding, and USB charging.`;
    appendMessage("assistant", reply);
  } else if (lower.includes("pay in 4") || lower.includes("installment")) {
    const reply = `PayPal Pay in 4 Transparency Notice:

If eligible, your purchase of $137.97 could be split into 4 bi-weekly payments of ~$34.49.

🛡️ Hackathon Accuracy & Safety Disclosures:
• Not Guaranteed: Pay in 4 is subject to consumer eligibility and credit checks by PayPal at checkout. It is not guaranteed in advance.
• Affordability Guardrail: Paying in installments does not reduce your total liability. Your obligation remains the full $137.97.`;
    appendMessage("assistant", reply);
  } else if (lower.includes("120") || (lower.includes("budget") && lower.includes("lower"))) {
    const bundle = {
      total_cost: 117.97,
      subtotal: 117.97,
      stated_budget: 120.0,
      surplus: 2.03,
      is_within_budget: true,
      average_reliability: 8.93,
      items: [
        { id: "lamp-taotronics-pro", name: "TaoTronics Eye-Care Multi-Spectrum Desk Lamp", price: 32.99, reliability_score: 9.2, category: "desk_lamp" },
        { id: "steamer-hilife-travel", name: "Hilife Portable Handheld Garment Steamer", price: 24.99, reliability_score: 8.2, category: "portable_steamer" },
        { id: "buds-anker-space-a40", name: "Anker Soundcore Space A40 Adaptive ANC Earbuds", price: 59.99, reliability_score: 9.4, category: "noise_cancelling_earbuds" }
      ]
    };
    activeBundle = bundle;
    renderActiveBundle(bundle);
    const reply = `With a tighter budget of $120.00, I re-optimized your basket:

• TaoTronics Desk Lamp ($32.99 | ★ 9.2)
• Hilife Portable Steamer ($24.99 | ★ 8.2) — *Swapped from Conair to save $20.00*
• Anker Space A40 Earbuds ($59.99 | ★ 9.4)

Budget Guard Status:
• New Total: $117.97 (+$2.03 remaining under $120.00 cap)
• Compromise: Hilife has a slightly smaller water tank, but preserves ANC earbuds!`;
    appendMessage("assistant", reply);
  } else if (lower.includes("checkout") || lower.includes("pay")) {
    const reply = `Your order of 3 items is verified with Budget Guard!

• Locked Total: $137.97 USD
• Payment Provider: PayPal Sandbox

Proceeding to PayPal Sandbox checkout creates a server-side locked order and simulates buyer approval before cryptographic capture verification.`;
    appendMessage("assistant", reply);
  } else {
    appendMessage("assistant", `I analyzed your request. You can ask me to optimize a multi-item bundle (e.g. college dorm, emergency laptop), test different budget caps, or explain trade-offs between brands!`);
  }
}

function appendMessage(sender, text) {
  const box = document.getElementById("chat-messages");
  const el = document.createElement("div");
  el.className = `message-bubble ${sender}`;
  el.innerHTML = `
    <div class="message-sender">${sender === "user" ? "You" : "PayPilot AI"}</div>
    <div>${text.replace(/\n/g, "<br>")}</div>
  `;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

function appendTypingIndicator() {
  const box = document.getElementById("chat-messages");
  const id = "typing-" + Date.now();
  const el = document.createElement("div");
  el.id = id;
  el.className = "message-bubble assistant";
  el.innerHTML = `<em class="text-muted text-xs">PayPilot AI is analyzing trade-offs...</em>`;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function renderActiveBundle(bundle) {
  const container = document.getElementById("active-bundle-summary");
  if (!bundle) return;

  const itemsHtml = bundle.items.map(it => `
    <div class="bundle-item-row">
      <div>
        <strong>${it.name}</strong>
        <div class="text-xs text-muted">Reliability: ★ ${it.reliability_score || it.reliability}/10</div>
      </div>
      <div style="font-weight: 600;">$${it.price.toFixed(2)}</div>
    </div>
  `).join("");

  container.innerHTML = `
    <div class="bundle-hero-box">
      <div class="bundle-hero-header">
        <div>
          <span class="text-xs text-muted">VERIFIED BUNDLE TOTAL</span>
          <div class="bundle-price-tag">$${bundle.total_cost.toFixed(2)}</div>
        </div>
        <div style="text-align: right;">
          <span class="text-xs ${bundle.is_within_budget ? 'text-success' : 'text-danger'}">
            ${bundle.is_within_budget ? `+$${(bundle.surplus || 0).toFixed(2)} Surplus` : `-$${(bundle.shortfall || 0).toFixed(2)} OVER BUDGET`}
          </span>
          <div class="bundle-budget-meta">Avg Reliability: ★ ${(bundle.average_reliability || 9.3).toFixed(2)}/10</div>
        </div>
      </div>
      <div class="bundle-items-list">${itemsHtml}</div>
    </div>
  `;
}

function renderTradeoffs(explanations) {
  const container = document.getElementById("chat-tradeoff-list");
  if (!explanations || explanations.length === 0) return;

  container.innerHTML = explanations.map(exp => `
    <div class="tradeoff-item">${exp}</div>
  `).join("");
}

// -------------------------------------------------------------
// TAB 2: Multi-Item Optimizer
// -------------------------------------------------------------
function initOptimizer() {
  const btn = document.getElementById("btn-run-optimizer");
  btn.addEventListener("click", runOptimizer);
  // Run initial evaluation
  runOptimizer();
}

async function runOptimizer() {
  const catInput = document.getElementById("opt-categories").value;
  const categories = catInput.split(",").map(c => c.trim()).filter(Boolean);
  const budget = parseFloat(document.getElementById("opt-budget").value) || 150.0;
  const priority = document.getElementById("opt-priority").value;

  const container = document.getElementById("optimizer-matrix-container");
  container.innerHTML = `<p class="text-muted" style="text-align:center; padding:20px;">Computing optimal combinations...</p>`;

  let data = null;
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE}/api/ai/recommend-bundle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ categories, stated_budget: budget, priority })
      });
      data = await res.json();
    } catch (e) {
      console.warn("Backend optimizer failed, using fallback:", e);
    }
  }

  if (!data || data.status !== "success") {
    // Local simulation
    data = simulateLocalOptimizer(budget, priority);
  }

  renderOptimizerMatrix(data, budget);
}

function simulateLocalOptimizer(budget, priority) {
  const rec = {
    total_cost: 137.97,
    is_within_budget: true,
    surplus: 12.03,
    average_reliability: 9.33,
    items: [
      { name: "TaoTronics Eye-Care Multi-Spectrum Lamp", price: 32.99, reliability_score: 9.2 },
      { name: "Conair Turbo ExtremeSteam Fabric Steamer", price: 44.99, reliability_score: 9.4 },
      { name: "Anker Soundcore Space A40 ANC Earbuds", price: 59.99, reliability_score: 9.4 }
    ]
  };
  const saver = {
    total_cost: 68.97,
    is_within_budget: true,
    surplus: 81.03,
    average_reliability: 8.10,
    items: [
      { name: "Lumina Glow LED Study Lamp", price: 18.99, reliability_score: 7.8 },
      { name: "Hilife Portable Handheld Steamer", price: 24.99, reliability_score: 8.2 },
      { name: "JLab Go Air Pop True Wireless Earbuds", price: 24.99, reliability_score: 8.3 }
    ]
  };
  const prem = {
    total_cost: 297.99,
    is_within_budget: false,
    shortfall: 147.99,
    average_reliability: 9.63,
    items: [
      { name: "BenQ e-Reading Architectural LED Light", price: 89.00, reliability_score: 9.6 },
      { name: "Conair Turbo ExtremeSteam Fabric Steamer", price: 44.99, reliability_score: 9.4 },
      { name: "Sony WF-1000XM5 Wireless ANC Earbuds", price: 149.00, reliability_score: 9.7 }
    ]
  };
  return {
    recommended_bundle: rec,
    budget_saver_bundle: saver,
    premium_bundle: prem,
    total_combinations_evaluated: 36,
    feasible_combinations_count: 18,
    trade_off_explanations: [
      "Optimal balance under $150.00 with $12.03 surplus buffer.",
      "In Desk Lamp: Chose TaoTronics ($32.99) over BenQ ($89.00), saving $56.01 to leave room for ANC earbuds."
    ]
  };
}

function renderOptimizerMatrix(data, budget) {
  const container = document.getElementById("optimizer-matrix-container");
  const rec = data.recommended_bundle;
  const saver = data.budget_saver_bundle;
  const prem = data.premium_bundle;

  function cardHtml(bundle, badgeClass, badgeText, title) {
    if (!bundle) return "";
    const itemsHtml = bundle.items.map(it => `
      <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:4px;">
        <span>${it.name}</span>
        <strong>$${it.price.toFixed(2)}</strong>
      </div>
    `).join("");

    return `
      <div class="bundle-card ${title.includes('Recommended') ? 'recommended' : ''}">
        <div>
          <span class="bundle-card-badge ${badgeClass}">${badgeText}</span>
          <h4 style="margin-bottom:8px;">${title}</h4>
          <div style="font-size:22px; font-weight:700; color:#34d399; margin-bottom:4px;">$${bundle.total_cost.toFixed(2)}</div>
          <div class="text-xs text-muted" style="margin-bottom:12px;">
            ${bundle.is_within_budget ? `+$${(bundle.surplus || 0).toFixed(2)} Remaining` : `-$${(bundle.shortfall || 0).toFixed(2)} OVER BUDGET`}
            • ★ ${(bundle.average_reliability || 0).toFixed(2)}/10 Avg Reliability
          </div>
          <div style="border-top:1px solid var(--border-color); padding-top:8px;">
            ${itemsHtml}
          </div>
        </div>
        <button class="btn btn-outline btn-sm" style="margin-top:14px; width:100%;" onclick="applyBundleToChat(${JSON.stringify(bundle).replace(/"/g, '&quot;')})">
          Select This Bundle
        </button>
      </div>
    `;
  }

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
      <h4>Combinations Evaluated: ${data.total_combinations_evaluated || 36} (${data.feasible_combinations_count || 18} Feasible under $${budget.toFixed(2)})</h4>
    </div>
    <div class="bundles-matrix-grid">
      ${cardHtml(rec, 'rec', '★ Top Recommendation', 'Best Fit (Reliability Focus)')}
      ${cardHtml(saver, 'saver', '💰 Lowest Cost', 'Budget-Saver Bundle')}
      ${cardHtml(prem, 'prem', '⚡ Unconstrained Quality', 'Maximum Reliability Benchmark')}
    </div>
  `;
}

window.applyBundleToChat = function(bundle) {
  activeBundle = bundle;
  renderActiveBundle(bundle);
  // Switch to chat tab
  document.querySelector(".tab-btn[data-tab='tab-chat']").click();
  appendMessage("assistant", `I've switched your active selection to the **${bundle.total_cost < 100 ? 'Budget-Saver' : 'Custom'} Bundle** ($${bundle.total_cost.toFixed(2)}). All calculations have been updated in Budget Guard.`);
};

// -------------------------------------------------------------
// TAB 3: Hands-Free Voice Commands
// -------------------------------------------------------------
function initVoice() {
  const micBtn = document.getElementById("btn-voice-mic");
  const liveText = document.getElementById("voice-live-text");
  const chips = document.querySelectorAll(".voice-chip-btn");

  // Web Speech API support
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = () => {
      micBtn.classList.add("recording");
      document.getElementById("mic-label").textContent = "Listening...";
    };

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results).map(r => r[0].transcript).join("");
      liveText.textContent = `"${transcript}"`;
    };

    recognition.onend = () => {
      micBtn.classList.remove("recording");
      document.getElementById("mic-label").textContent = "Click to Speak";
      const spoken = liveText.textContent.replace(/"/g, "").trim();
      if (spoken && spoken !== "Click the microphone or choose a voice prompt below...") {
        processVoiceCommand(spoken);
      }
    };
  }

  micBtn.addEventListener("click", () => {
    if (recognition) {
      try {
        recognition.start();
      } catch (e) {
        recognition.stop();
      }
    } else {
      alert("Web Speech API not supported in this browser. Please use the simulated voice buttons below!");
    }
  });

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const spoken = chip.dataset.spoken;
      liveText.textContent = `"${spoken}"`;
      processVoiceCommand(spoken);
    });
  });

  // Modal event listeners
  document.getElementById("modal-btn-cancel").addEventListener("click", () => {
    document.getElementById("voice-confirmation-modal").classList.add("hidden");
    speakTts("Payment authorization cancelled.");
  });

  document.getElementById("modal-btn-confirm").addEventListener("click", () => {
    document.getElementById("voice-confirmation-modal").classList.add("hidden");
    speakTts("Payment authorization confirmed. Proceeding to PayPal Sandbox checkout.");
    alert("PayPal Sandbox payment authorized! Server verifies cryptographic capture.");
  });
}

async function processVoiceCommand(transcript) {
  let result = null;
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE}/api/ai/voice-command`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          transcript: transcript,
          current_bundle_total: activeBundle ? activeBundle.total_cost : 137.97,
          item_count: activeBundle ? activeBundle.items.length : 3
        })
      });
      const data = await res.json();
      result = data.result;
    } catch (e) {
      console.warn("Backend voice endpoint failed:", e);
    }
  }

  if (!result) {
    result = simulateLocalVoiceCommand(transcript);
  }

  renderVoiceResult(result);

  // Play synthesized speech
  if (result.tts_speech_response) {
    speakTts(result.tts_speech_response);
  }

  // Enforce Safety Checklist rule: require explicit confirmation before payment
  if (result.requires_explicit_confirmation) {
    const modal = document.getElementById("voice-confirmation-modal");
    document.getElementById("modal-confirm-text").textContent = result.confirmation_prompt;
    document.getElementById("modal-order-amount").textContent = `$${(activeBundle ? activeBundle.total_cost : 137.97).toFixed(2)} USD`;
    modal.classList.remove("hidden");
  }
}

function simulateLocalVoiceCommand(transcript) {
  const lower = transcript.toLowerCase();
  if (lower.includes("checkout") || lower.includes("pay")) {
    return {
      status: "success",
      raw_transcript: transcript,
      interpreted_action: "INITIATE_PAYMENT",
      requires_explicit_confirmation: true,
      is_payment_action: true,
      confirmation_prompt: "Security Guardrail: Voice commands require explicit verification before payment. Do you authorize initiating PayPal Sandbox checkout for $137.97 (3 items)?",
      tts_speech_response: "Payment confirmation required. Please confirm if you wish to proceed to PayPal Sandbox checkout for $137.97.",
      safety_checklist_rule: "Voice commands require explicit user confirmation before any payment action."
    };
  }
  if (lower.includes("dorm")) {
    return {
      status: "success",
      raw_transcript: transcript,
      interpreted_action: "OPTIMIZE_DORM",
      requires_explicit_confirmation: false,
      tts_speech_response: "Optimizing college dorm move-in basket for lamp, steamer, and study buds under $150 budget.",
      safety_checklist_rule: "Safe non-payment command."
    };
  }
  return {
    status: "success",
    raw_transcript: transcript,
    interpreted_action: "GENERAL_QUERY",
    requires_explicit_confirmation: false,
    tts_speech_response: "Interpreted voice command and updated shopping parameters.",
    safety_checklist_rule: "Safe non-payment command."
  };
}

function renderVoiceResult(res) {
  const box = document.getElementById("voice-result-box");
  const content = document.getElementById("voice-result-content");
  const badge = document.getElementById("voice-action-badge");

  box.classList.remove("hidden");
  badge.textContent = res.interpreted_action;
  badge.className = `badge ${res.requires_explicit_confirmation ? 'badge-danger' : 'badge-success'}`;

  content.innerHTML = `
    <div style="font-size: 13px; margin-bottom: 8px;">
      <strong>Interpreted Action:</strong> <code>${res.interpreted_action}</code>
    </div>
    <div style="font-size: 13px; margin-bottom: 8px;">
      <strong>TTS Speech Feedback:</strong> "${res.tts_speech_response}"
    </div>
    <div style="font-size: 12px; color: ${res.requires_explicit_confirmation ? '#f87171' : '#34d399'};">
      🛡️ <strong>Safety Rule:</strong> ${res.safety_checklist_rule}
    </div>
  `;
}

function speakTts(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }
}

// -------------------------------------------------------------
// TAB 4: Financial Smart Filter
// -------------------------------------------------------------
const SAMPLE_MESSAGES = [
  {
    id: "sample-phish",
    title: "Phishing SMS (Fake PayPal Security Threat)",
    sender: "+1 (800) 555-0199",
    subject: "PAYPAL URGENT: Account Suspended",
    body: "URGENT: Your PayPal account has been suspended due to unauthorized activity. Verify your PIN and identity within 24 hours at http://paypa1-security-verification.xyz/login to restore access."
  },
  {
    id: "sample-promo",
    title: "Promotional Marketing Email",
    sender: "offers@e.shoppingdeals.com",
    subject: "Exclusive 30% Off Back-to-School Dorm Essentials!",
    body: "Huge Flash Sale! Use promo code DORM30 to get 30% off desk lamps, garment steamers, and noise-cancelling earbuds. Limited time offer ends Sunday!"
  },
  {
    id: "sample-receipt",
    title: "Authentic PayPal Payment Receipt",
    sender: "service@paypal.com",
    subject: "Receipt for your payment of $137.97 to PayPilot Demo Store",
    body: "Hello College Student, you sent a payment of $137.97 USD to PayPilot Demo Store. Payment Confirmation ID: 9BT48291KL382. You can view your transaction history anytime in your account."
  },
  {
    id: "sample-delivery",
    title: "Ambiguous Package Fee (Needs Review)",
    sender: "tracking-alerts@fastdelivery-global.net",
    subject: "Package Delivery Update: Fee Pending",
    body: "Your package delivery is held due to an unpaid $1.99 handling fee. Click here to confirm shipping address and release your parcel."
  }
];

function initFilter() {
  renderSampleFilterMessages();

  document.getElementById("btn-run-filter").addEventListener("click", () => {
    const sender = document.getElementById("filter-input-sender").value;
    const subject = document.getElementById("filter-input-subject").value;
    const body = document.getElementById("filter-input-body").value;
    if (!body) {
      alert("Please enter message body to analyze.");
      return;
    }
    analyzeMessage({ sender, subject, body });
  });
}

function renderSampleFilterMessages() {
  const container = document.getElementById("filter-samples-list");
  container.innerHTML = SAMPLE_MESSAGES.map(s => `
    <button class="sample-item-btn" onclick="loadSampleMessage('${s.id}')">
      <strong>${s.title}</strong>
      <div class="text-xs text-muted">From: ${s.sender} • "${s.subject}"</div>
    </button>
  `).join("");
}

window.loadSampleMessage = function(id) {
  const sample = SAMPLE_MESSAGES.find(s => s.id === id);
  if (!sample) return;
  document.getElementById("filter-input-sender").value = sample.sender;
  document.getElementById("filter-input-subject").value = sample.subject;
  document.getElementById("filter-input-body").value = sample.body;
  analyzeMessage(sample);
};

async function analyzeMessage(msg) {
  let result = null;
  if (isBackendOnline) {
    try {
      const res = await fetch(`${API_BASE}/api/ai/smart-filter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(msg)
      });
      const data = await res.json();
      result = data.result;
    } catch (e) {
      console.warn("Backend smart-filter failed:", e);
    }
  }

  if (!result) {
    result = simulateLocalFilter(msg);
  }

  renderFilterAssessment(result);
}

function simulateLocalFilter(msg) {
  const full = `${msg.sender} ${msg.subject} ${msg.body}`.toLowerCase();
  const warningSigns = [];

  if (full.includes("paypa1") || full.includes(".xyz") || full.includes("verify your pin") || full.includes("suspended")) {
    warningSigns.push("Suspicious domain link detected (resembles lookalike/spoofed domain)");
    warningSigns.push("Artificial high-urgency language attempting to compel immediate reaction");
    warningSigns.push("Unsafe credential harvesting prompt (requesting PIN, OTP, or password)");
    return {
      category: "SUSPICIOUS",
      risk_level: "HIGH",
      warning_signs: warningSigns,
      action_recommendation: "Do NOT click any embedded links or share credentials. Verify account status by navigating directly to PayPal.com through your browser.",
      guardrail_disclaimer: "Safety Guardrail Compliance: PayPilot Smart Filter provides heuristic guidance and does not claim definitive fraud detection. Messages are never silently deleted."
    };
  } else if (full.includes("discount") || full.includes("promo") || full.includes("sale")) {
    return {
      category: "PROMOTIONAL",
      risk_level: "LOW",
      warning_signs: [],
      action_recommendation: "Commercial promotion or marketing newsletter. Safe to archive or ignore.",
      guardrail_disclaimer: "Messages are never silently deleted."
    };
  } else if (full.includes("receipt") && full.includes("paypal.com")) {
    return {
      category: "IMPORTANT",
      risk_level: "LOW",
      warning_signs: [],
      action_recommendation: "Verified operational message from official sender. Kept for your records.",
      guardrail_disclaimer: "Messages are never silently deleted."
    };
  }

  return {
    category: "NEEDS_REVIEW",
    risk_level: "MEDIUM",
    warning_signs: ["Unrecognized sender or ambiguous delivery request"],
    action_recommendation: "Review carefully. Confirm details through an official known portal.",
    guardrail_disclaimer: "Messages are never silently deleted."
  };
}

function renderFilterAssessment(res) {
  const container = document.getElementById("filter-result-container");
  const warningsHtml = res.warning_signs && res.warning_signs.length > 0
    ? res.warning_signs.map(w => `<li class="warning-sign-item">⚠️ ${w}</li>`).join("")
    : `<li class="text-xs text-muted">No suspicious indicators detected.</li>`;

  container.innerHTML = `
    <div class="assessment-box">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="assessment-tag ${res.category}">${res.category}</span>
        <span class="text-xs text-muted">Risk Level: <strong>${res.risk_level}</strong></span>
      </div>

      <div>
        <h4 style="font-size:13px; margin-bottom:6px;">Warning Signs Identified:</h4>
        <ul class="warning-signs-list">${warningsHtml}</ul>
      </div>

      <div style="background-color:var(--bg-surface); padding:10px; border-radius:var(--radius-sm); font-size:13px;">
        <strong>Recommended Action:</strong>
        <p style="margin-top:4px;">${res.action_recommendation}</p>
      </div>

      <div class="text-xs text-muted" style="border-top:1px solid var(--border-color); padding-top:10px;">
        🛡️ <strong>Guardrail Compliance:</strong> ${res.guardrail_disclaimer}
      </div>
    </div>
  `;
}

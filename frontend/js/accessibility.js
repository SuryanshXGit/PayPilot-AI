/**
 * PayPilot AI — Adaptive Universal Accessibility Controller
 * Module: Meenal (Universal Accessibility Owner)
 *
 * Implements:
 * 1. High contrast mode (WCAG AAA compliant color ratios, clear borders)
 * 2. Scalable text sizing (Standard, Medium 120%, Large 140%)
 * 3. Text-to-Speech (TTS) using Web Speech Synthesis API
 * 4. Keyboard navigation, visible focus indicators & keyboard shortcuts modal
 * 5. Screen reader live announcement channel (aria-live)
 */

class AccessibilityController {
  constructor() {
    this.highContrast = localStorage.getItem("paypilot_high_contrast") === "true";
    this.textScale = localStorage.getItem("paypilot_text_scale") || "100"; // 100, 120, 140
    this.speechSynth = window.speechSynthesis || null;
    this.isSpeaking = false;
    this.currentUtterance = null;

    this.init();
  }

  init() {
    // Apply saved high contrast
    if (this.highContrast) {
      document.documentElement.classList.add("high-contrast");
    }

    // Apply saved text scale
    this.applyTextScale(this.textScale);

    // Setup keyboard listener
    window.addEventListener("keydown", (e) => this.handleGlobalKeydown(e));
  }

  // -------------------------------------------------------------------------
  // 1. HIGH CONTRAST MODE
  // -------------------------------------------------------------------------
  toggleHighContrast() {
    this.highContrast = !this.highContrast;
    if (this.highContrast) {
      document.documentElement.classList.add("high-contrast");
      this.announce("High contrast mode enabled", "polite");
    } else {
      document.documentElement.classList.remove("high-contrast");
      this.announce("Standard contrast mode enabled", "polite");
    }
    localStorage.setItem("paypilot_high_contrast", this.highContrast);
    this.updateToggleButtons();
    return this.highContrast;
  }

  // -------------------------------------------------------------------------
  // 2. SCALABLE TEXT (100%, 120%, 140%)
  // -------------------------------------------------------------------------
  applyTextScale(scale) {
    this.textScale = scale;
    document.documentElement.classList.remove("text-scale-100", "text-scale-120", "text-scale-140");
    document.documentElement.classList.add(`text-scale-${scale}`);
    localStorage.setItem("paypilot_text_scale", scale);
    this.updateScaleButtons();
  }

  cycleTextScale() {
    if (this.textScale === "100") {
      this.applyTextScale("120");
      this.announce("Text size scaled to 120 percent", "polite");
    } else if (this.textScale === "120") {
      this.applyTextScale("140");
      this.announce("Text size scaled to 140 percent", "polite");
    } else {
      this.applyTextScale("100");
      this.announce("Text size reset to standard 100 percent", "polite");
    }
  }

  // -------------------------------------------------------------------------
  // 3. TEXT-TO-SPEECH (TTS)
  // -------------------------------------------------------------------------
  speak(text, onEnd = null) {
    if (!this.speechSynth) {
      this.announce("Text-to-speech is not supported in this browser.", "assertive");
      return;
    }

    this.stopSpeaking();

    // Clean markdown or raw symbols for clean speech
    const cleanText = text
      .replace(/[*_#`~]/g, "")
      .replace(/\$/g, " dollars ")
      .replace(/\/10/g, " out of 10")
      .trim();

    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.updateTTSButtons();
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.updateTTSButtons();
      if (onEnd) onEnd();
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.updateTTSButtons();
    };

    this.currentUtterance = utterance;
    this.speechSynth.speak(utterance);
  }

  stopSpeaking() {
    if (this.speechSynth && (this.speechSynth.speaking || this.speechSynth.pending)) {
      this.speechSynth.cancel();
    }
    this.isSpeaking = false;
    this.updateTTSButtons();
  }

  readElement(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText || el.textContent;
    this.speak(text);
  }

  readCurrentSummary() {
    const summaryEl = document.getElementById("bundle-summary-text") ||
                      document.getElementById("budget-guard-banner") ||
                      document.getElementById("tradeoff-explanation-box");
    if (summaryEl) {
      this.speak(summaryEl.innerText || summaryEl.textContent);
    } else {
      this.speak("PayPilot AI shopping dashboard. Enter your budget and items to start.");
    }
  }

  // -------------------------------------------------------------------------
  // 4. SCREEN READER LIVE ANNOUNCEMENTS
  // -------------------------------------------------------------------------
  announce(message, priority = "polite") {
    const announcer = document.getElementById("sr-announcer");
    if (!announcer) return;

    announcer.setAttribute("aria-live", priority);
    announcer.textContent = "";
    setTimeout(() => {
      announcer.textContent = message;
    }, 50);
  }

  // -------------------------------------------------------------------------
  // 5. KEYBOARD NAVIGATION & SHORTCUTS
  // -------------------------------------------------------------------------
  handleGlobalKeydown(e) {
    // Alt + H : Toggle High Contrast
    if (e.altKey && (e.key === "h" || e.key === "H")) {
      e.preventDefault();
      this.toggleHighContrast();
    }
    // Alt + T : Cycle Text Size
    if (e.altKey && (e.key === "t" || e.key === "T")) {
      e.preventDefault();
      this.cycleTextScale();
    }
    // Alt + R : Read Aloud Summary / Stop
    if (e.altKey && (e.key === "r" || e.key === "R")) {
      e.preventDefault();
      if (this.isSpeaking) {
        this.stopSpeaking();
      } else {
        this.readCurrentSummary();
      }
    }
    // Alt + K : Open Shortcuts Modal
    if (e.altKey && (e.key === "k" || e.key === "K")) {
      e.preventDefault();
      const modal = document.getElementById("shortcuts-modal");
      if (modal) modal.classList.toggle("hidden");
    }
    // Escape : Close any open modal
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay:not(.hidden)").forEach(m => m.classList.add("hidden"));
    }
  }

  updateToggleButtons() {
    const btn = document.getElementById("btn-high-contrast");
    if (btn) {
      btn.setAttribute("aria-pressed", this.highContrast ? "true" : "false");
      btn.classList.toggle("active", this.highContrast);
    }
  }

  updateScaleButtons() {
    const btn = document.getElementById("btn-text-scale");
    if (btn) {
      btn.innerText = `A ${this.textScale}%`;
      btn.setAttribute("aria-label", `Text scale currently ${this.textScale} percent. Click to cycle size.`);
    }
  }

  updateTTSButtons() {
    const btn = document.getElementById("btn-tts");
    if (btn) {
      if (this.isSpeaking) {
        btn.classList.add("active-speaking");
        btn.innerHTML = `<span class="icon">⏹️</span> <span>Stop Speech</span>`;
        btn.setAttribute("aria-label", "Stop speech playback");
      } else {
        btn.classList.remove("active-speaking");
        btn.innerHTML = `<span class="icon">🔊</span> <span>Read Aloud</span>`;
        btn.setAttribute("aria-label", "Read aloud current recommendations and budget status");
      }
    }
  }
}

// Global instance
const a11y = new AccessibilityController();
if (typeof window !== "undefined") {
  window.a11y = a11y;
}

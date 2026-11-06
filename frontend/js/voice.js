/**
 * PayPilot AI — Hands-Free Voice Commands Controller
 * Module: Suryansh (Hands-Free Voice Interface)
 *
 * Implements:
 * 1. Speech-to-Text input using Web Speech Recognition API
 * 2. Visual interpreted request feedback container
 * 3. Command dispatcher for navigation, quick-fill scenarios, and accessibility
 * 4. Explicit confirmation modal before any payment-related action
 */

class VoiceController {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
    this.isListening = false;

    if (this.recognition) {
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = "en-US";

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateMicButton();
        this.showTranscript("Listening... speak your request (e.g. 'Dorm move-in', 'Check budget', 'High contrast')");
      };

      this.recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join("");
        this.showTranscript(`"${transcript}"`);
        if (event.results[0].isFinal) {
          this.processVoiceCommand(transcript.trim().toLowerCase());
        }
      };

      this.recognition.onerror = (event) => {
        this.isListening = false;
        this.updateMicButton();
        this.showTranscript(`Voice recognition error: ${event.error}`);
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateMicButton();
      };
    }
  }

  toggleListening() {
    if (!this.recognition) {
      alert("Voice recognition is not supported in this browser. Please use Chrome, Edge, or a Web Speech-supported browser.");
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }

  showTranscript(msg) {
    const box = document.getElementById("voice-transcript-banner");
    if (box) {
      box.textContent = msg;
      box.classList.remove("hidden");
    }
  }

  processVoiceCommand(command) {
    if (window.a11y) {
      window.a11y.announce(`Processing voice command: ${command}`, "polite");
    }

    // Navigation and demo quick-fill commands
    if (command.includes("dorm") || command.includes("college") || command.includes("150")) {
      this.showTranscript(`Command recognized: Loading Dorm Move-In scenario ($150 budget)...`);
      if (window.app) window.app.loadDormScenario();
    } else if (command.includes("emergency") || command.includes("laptop") || command.includes("broken")) {
      this.showTranscript(`Command recognized: Loading Emergency Expense scenario ($500 budget)...`);
      if (window.app) window.app.loadEmergencyScenario();
    } else if (command.includes("high contrast") || command.includes("contrast")) {
      this.showTranscript(`Command recognized: Toggling high contrast mode.`);
      if (window.a11y) window.a11y.toggleHighContrast();
    } else if (command.includes("text") || command.includes("font") || command.includes("scale") || command.includes("larger") || command.includes("bigger")) {
      this.showTranscript(`Command recognized: Cycling text scale.`);
      if (window.a11y) window.a11y.cycleTextScale();
    } else if (command.includes("read") || command.includes("speak") || command.includes("listen")) {
      this.showTranscript(`Command recognized: Reading aloud summary.`);
      if (window.a11y) window.a11y.readCurrentSummary();
    } else if (command.includes("stop") || command.includes("quiet") || command.includes("shut")) {
      this.showTranscript(`Command recognized: Stopping speech playback.`);
      if (window.a11y) window.a11y.stopSpeaking();
    } else if (command.includes("bill") || command.includes("finances")) {
      this.showTranscript(`Command recognized: Opening Financial Health & Bills manager.`);
      if (window.app) window.app.openBillsModal();
    } else if (command.includes("check budget") || command.includes("calculate") || command.includes("optimize")) {
      this.showTranscript(`Command recognized: Recalculating Budget Guard.`);
      if (window.budgetGuardUI) window.budgetGuardUI.recalculateCurrentBundle();
    } else if (command.includes("pay") || command.includes("checkout") || command.includes("buy")) {
      // Guardrail: Explicit confirmation before payment action
      this.showTranscript(`Payment command detected. Requiring explicit user confirmation before checkout...`);
      this.requestPaymentConfirmation();
    } else {
      this.showTranscript(`Interpreted: "${command}". (Tip: Try 'Dorm Move-in', 'Emergency Laptop', 'Check budget', or 'High contrast')`);
    }
  }

  requestPaymentConfirmation() {
    const confirmModal = document.getElementById("voice-confirm-modal");
    if (confirmModal) {
      confirmModal.classList.remove("hidden");
      if (window.a11y) {
        window.a11y.speak("Voice payment request detected. Please click Confirm or say confirm to proceed to PayPal Sandbox checkout.");
      }
    } else {
      if (confirm("Proceed to PayPal Sandbox checkout with current bundle?")) {
        if (window.paypalCheckoutUI) window.paypalCheckoutUI.initiateCheckout();
      }
    }
  }

  updateMicButton() {
    const btn = document.getElementById("btn-voice-mic");
    if (btn) {
      if (this.isListening) {
        btn.classList.add("active-listening");
        btn.setAttribute("aria-label", "Listening for voice command... Click to stop.");
      } else {
        btn.classList.remove("active-listening");
        btn.setAttribute("aria-label", "Activate hands-free voice commands");
      }
    }
  }
}

// Global instance
const voice = new VoiceController();
if (typeof window !== "undefined") {
  window.voice = voice;
}

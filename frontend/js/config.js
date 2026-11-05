/**
 * PayPilot AI — Configuration
 * Module: Meenal (Frontend)
 */

const CONFIG = {
  // Backend API base URL (Flask server run by Jaskaran / Suryansh)
  API_BASE_URL: "http://127.0.0.1:5001",

  // Timeout for API requests in milliseconds
  API_TIMEOUT_MS: 15000,

  // Reference date for date calculations (Hackathon current local date)
  REFERENCE_DATE: "2026-11-04",

  // Default College Dorm Demo scenario params
  DEFAULT_DORM_BUDGET: 150.00,
  DEFAULT_DORM_CATEGORIES: ["desk_lamp", "portable_steamer", "noise_cancelling_earbuds"],

  // Emergency Laptop Demo scenario params
  DEFAULT_EMERGENCY_BUDGET: 500.00,
  DEFAULT_EMERGENCY_CATEGORY: "laptop",

  // Currency code
  CURRENCY: "USD",
  CURRENCY_SYMBOL: "$",

  // PayPal Sandbox configuration
  PAYPAL_SANDBOX_CLIENT_ID: "sb-paypilot-demo-client-id",
  PAYPAL_ENV: "sandbox"
};

if (typeof window !== "undefined") {
  window.CONFIG = CONFIG;
}

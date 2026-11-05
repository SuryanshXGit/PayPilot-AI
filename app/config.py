import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv("SECRET_KEY", "paypilot-ai-hackathon-secret-key-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT = int(os.getenv("PORT", 5001))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "paypilot.db"))
    CORS_ORIGINS = os.getenv("FRONTEND_ORIGIN", "*")

    # Currency and calculation constants
    DEFAULT_CURRENCY = "USD"
    DEFAULT_TAX_RATE = 0.08  # 8% estimated standard sales tax
    FREE_SHIPPING_THRESHOLD = 35.00  # Orders over $35 get free standard shipping
    STANDARD_SHIPPING_FEE = 4.99

    # PayPal Sandbox Configuration (Owned by Suryansh)
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_ENV = os.getenv("PAYPAL_ENV", "sandbox")
    PAYPAL_API_BASE = os.getenv("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com")
    PAYPAL_RETURN_URL = os.getenv("PAYPAL_RETURN_URL", "http://localhost:3000/checkout/success")
    PAYPAL_CANCEL_URL = os.getenv("PAYPAL_CANCEL_URL", "http://localhost:3000/checkout/cancel")


class TestConfig(Config):
    """Configuration for testing with an in-memory database or temporary file."""
    TESTING = True
    DATABASE_PATH = ":memory:"
    DEBUG = False

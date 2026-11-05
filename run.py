import os
from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"🚀 PayPilot AI Backend running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

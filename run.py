import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"[*] Starting AI Skill Verification Platform on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)

import os
import json

def load_ai_config() -> dict:
    """Load AI settings from the main config.json."""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "config.json"
    )
    with open(config_path, "r") as f:
        config = json.load(f)
        return config.get("ai", {
            "model": "gemini-2.5-pro",
            "rate_limit_delay_seconds": 2,
            "max_retries": 3
        })

AI_CONFIG = load_ai_config()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY environment variable is not set.")

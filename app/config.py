import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "FitBuddy")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./fitbuddy.db"
)

# Gemini configuration. Ignore the example value commonly left in .env so
# DEMO_MODE=true works without a real API key.
_PLACEHOLDER_API_KEYS = {
    "your_gemini_api_key_here",
    "your_api_key_here",
    "replace_with_your_api_key",
}


def _get_gemini_api_key():
    for value in (
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
    ):
        key = (value or "").strip()
        if key and key.casefold() not in _PLACEHOLDER_API_KEYS:
            return key
    return None


GEMINI_API_KEY = _get_gemini_api_key()

# Keep model names configurable because Google can change
# model availability over time.
GEMINI_WORKOUT_MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-flash"
)

GEMINI_TIP_MODEL = os.getenv(
    "GEMINI_TIP_MODEL",
    "gemini-2.5-flash"
)

# Demo mode allows the project to run without Gemini API.
DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).lower() in {
    "1",
    "true",
    "yes",
    "on"
}

# Simple admin key for the college project.
ADMIN_KEY = os.getenv(
    "ADMIN_KEY",
    "fitbuddy-admin"
)

# src/config.py
import os

# Required: the app should fail fast at startup if these are missing
DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]

# Optional: sensible defaults, overridable per environment
RATE_LIMIT_COUNT = int(os.environ.get("RATE_LIMIT_COUNT", 10))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))  # seconds
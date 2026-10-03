# src/config.py
import logging
import os

from src.logger import get_logger

log = get_logger(__name__)


def _require(key: str) -> str:
    """Read a required env var; log CRITICAL and raise if it is missing."""
    val = os.environ.get(key)
    if not val:
        log.critical("missing_env_var", key=key)
        raise RuntimeError(f"Required environment variable {key!r} is not set")
    return val


DATABASE_URL = _require("DATABASE_URL")
REDIS_URL = _require("REDIS_URL")

# Optional — overridable per environment via Render's env-var panel
RATE_LIMIT_COUNT = int(os.environ.get("RATE_LIMIT_COUNT", 10))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))  # seconds
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
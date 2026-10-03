# src/redis_client.py
import re

import redis

from src.config import REDIS_URL
from src.logger import get_logger

log = get_logger(__name__)


def _redact_url(url: str) -> str:
    """Replace the password in a Redis URL with '***' before logging."""
    return re.sub(r"(?<=://)([^:]+):([^@]+)@", r"\1:***@", url)


redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Best-effort connectivity check at startup — log only, never crash the app.
# The rate_limiter already has fail-open behaviour for runtime Redis errors.
try:
    redis_client.ping()
    log.info("redis_client_created", url=_redact_url(REDIS_URL))
except redis.exceptions.RedisError:
    log.error("redis_unreachable_at_startup", url=_redact_url(REDIS_URL), exc_info=True)
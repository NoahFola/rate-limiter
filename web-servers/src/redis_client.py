# src/redis_client.py
import re

import redis

from src.config import REDIS_URL
from src.logger import get_logger

log = get_logger(__name__)


def _redact_url(url: str) -> str:
    """Replace the password in a Redis URL with '***' before logging."""
    return re.sub(r"(?<=://)([^:]+):([^@]+)@", r"\1:***@", url)


try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    # Verify connectivity eagerly so startup logs capture a broken Redis URL.
    redis_client.ping()
    log.info("redis_client_created", url=_redact_url(REDIS_URL))
except redis.exceptions.RedisError:
    log.error("redis_client_failed", url=_redact_url(REDIS_URL), exc_info=True)
    raise
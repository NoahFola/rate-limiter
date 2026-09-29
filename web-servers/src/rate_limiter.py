# src/rate_limiter.py
import time
import uuid

import redis
from flask import request, jsonify

from src.config import RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW
from src.redis_client import redis_client


def rate_limiter():
    """Runs before every request. Returning a response blocks it; returning None lets it through."""
    key = f"rate_limit:{request.remote_addr}"
    now = time.time()

    try:
        # 1. Drop old entries, then count what's left in the window
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - RATE_LIMIT_WINDOW)
        pipe.zcard(key)
        _, count = pipe.execute()

        # 2. Over the limit? Reject WITHOUT recording this request
        if count >= RATE_LIMIT_COUNT:
            return (
                jsonify(error="Too many requests"),
                429,
                {"Retry-After": str(RATE_LIMIT_WINDOW)},
            )

        # 3. Allowed: record it
        pipe = redis_client.pipeline()
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        pipe.expire(key, RATE_LIMIT_WINDOW)
        pipe.execute()

    except redis.exceptions.RedisError:
        # Redis is down: fail open (let the request through)
        return None
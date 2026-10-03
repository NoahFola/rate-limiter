# app.py
# configure_logging() must run before any other src import so that
# every module's module-level logger picks up the right processors.
from src.logger import configure_logging, get_logger

configure_logging()

import os

from flask import Flask, jsonify

from src.db import init_db
from src.rate_limiter import rate_limiter
from src.redis_client import redis_client
from src.routes import bp

log = get_logger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Rate limiter ────────────────────────────────────────────────────────
    app.before_request(rate_limiter)

    # ── Routes ──────────────────────────────────────────────────────────────
    app.register_blueprint(bp)

    # ── Global error handler ─────────────────────────────────────────────────
    @app.errorhandler(Exception)
    def handle_unexpected_error(exc):
        log.error("unhandled_exception", exc_info=True)
        return jsonify(error="Internal server error"), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Initialise DB schema then start the dev server.
    try:
        init_db()
    except Exception:
        log.error("db_init_failed", exc_info=True)
        raise

    log.info("app_started", port=5000)
    app.run(host="0.0.0.0", port=5000)
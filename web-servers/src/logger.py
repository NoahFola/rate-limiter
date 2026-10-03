# src/logger.py
import logging
import os

import structlog


def configure_logging() -> None:
    """Configure structlog to emit structured JSON lines to stdout.

    Call this once, at the very top of app.py, before anything else is
    imported that might create a logger.
    """
    log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        format="%(message)s",   # structlog handles the full formatting
        level=log_level,
    )

    structlog.configure(
        processors=[
            # Merge any thread-local context bound via structlog.contextvars
            structlog.contextvars.merge_contextvars,
            # Add the log level name ("info", "warning", …)
            structlog.stdlib.add_log_level,
            # Add the logger name (module path passed to get_logger)
            structlog.stdlib.add_logger_name,
            # Human-readable ISO-8601 timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Render exception info when exc_info=True is passed
            structlog.processors.format_exc_info,
            # Render the final dict as a single-line JSON string
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structlog logger bound to *name* (pass __name__)."""
    return structlog.get_logger(name)

# src/db.py
import psycopg2

from src.config import DATABASE_URL
from src.logger import get_logger

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

log = get_logger(__name__)


@retry(
    retry=retry_if_exception_type(psycopg2.OperationalError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(4),
    before_sleep=lambda rs: log.warning(
        "db_connect_retry",
        attempt=rs.attempt_number,
        wait=rs.next_action.sleep,
    ),
    reraise=True,
)
def get_db_connection():
    """Open a new connection. The caller is responsible for closing it."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        log.debug("db_connection_opened")
        return conn
    except Exception:
        log.error("db_connection_failed", exc_info=True)
        raise


def init_db():
    """Create the urls table if it doesn't exist yet."""
    log.info("db_init_start")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id           SERIAL PRIMARY KEY,
                short_code   VARCHAR(10) UNIQUE NOT NULL,
                original_url TEXT NOT NULL,
                created_at   TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()      # success: save
        log.info("db_schema_ensured")
    except Exception:
        conn.rollback()    # failure: undo
        log.error("db_schema_failed", exc_info=True)
        raise              # re-raise so the error isn't hidden
    finally:
        cur.close()        # always close the cursor
        conn.close()       # always close the connection
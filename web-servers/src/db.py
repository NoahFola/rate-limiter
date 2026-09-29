# src/db.py
import psycopg2
from src.config import DATABASE_URL


def get_db_connection():
    """Open a new connection. The caller is responsible for closing it."""
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create the urls table if it doesn't exist yet."""
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
    except Exception:
        conn.rollback()    # failure: undo
        raise              # re-raise so the error isn't hidden
    finally:
        cur.close()        # always close the cursor
        conn.close()       # always close the connection
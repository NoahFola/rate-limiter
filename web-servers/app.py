import psycopg2
import string
import random
import redis
import time
from flask import Flask, request, redirect, jsonify
import os

app = Flask(__name__)



DATABASE_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# --- Rate Limiter Settings ---
RATE_LIMIT_COUNT = 10  # 10 requests
RATE_LIMIT_WINDOW = 60 # per 60 seconds

# Establish a reusable Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

@app.before_request
def rate_limiter():
    # Use the user's IP address as the key
    # In a real app, you'd handle proxies via request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    key = f"rate_limit:{request.remote_addr}"
    now = time.time()

    # Use a Redis pipeline for atomic operations
    pipe = redis_client.pipeline()
    # 1. Add current request timestamp. The score and member are the same.
    pipe.zadd(key, {str(now): now})
    # 2. Remove all timestamps older than our window
    pipe.zremrangebyscore(key, 0, now - RATE_LIMIT_WINDOW)
    # 3. Get the count of remaining timestamps
    pipe.zcard(key)
    # 4. Set an expiration on the key so it cleans itself up
    pipe.expire(key, RATE_LIMIT_WINDOW)

    # Execute the pipeline and get the results
    results = pipe.execute()
    request_count = results[2] # The result of the zcard command

    if request_count > RATE_LIMIT_COUNT:
        # Return a 429 Too Many Requests error
        return jsonify(error="Rate limit exceeded"), 429

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            short_code VARCHAR(6) UNIQUE NOT NULL,
            original_url TEXT NOT NULL
        );
    ''')
    # Check if the index exists before creating it
    cur.execute('''
        SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = 'idx_original_url' AND n.nspname = 'public';
    ''')
    if cur.fetchone() is None:
        cur.execute('CREATE INDEX idx_original_url ON urls (original_url);')
    conn.commit()
    cur.close()
    conn.close()

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/", methods=['GET'])
def index():
    return "URL Shortener is running!\n", 200

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT short_code FROM urls WHERE original_url = %s", (original_url,))
    existing_url = cur.fetchone()

    if existing_url:
        short_code = existing_url[0]
    else:
        short_code = generate_short_code()
        cur.execute("INSERT INTO urls (short_code, original_url) VALUES (%s, %s)", (short_code, original_url))
        conn.commit()

    cur.close()
    conn.close()

    return jsonify(short_url=f"/{short_code}")

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT original_url FROM urls WHERE short_code = %s", (short_code,))
    url_record = cur.fetchone()
    cur.close()
    conn.close()

    if url_record:
        return redirect(url_record[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db() 
    app.run(host='0.0.0.0', port=5000)  
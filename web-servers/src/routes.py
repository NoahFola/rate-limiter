# src/routes.py
from urllib.parse import urlparse

import psycopg2.errors
from flask import Blueprint, jsonify, redirect, request

from src.db import get_db_connection
from src.utils import generate_short_code

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return jsonify(message="URL shortener is running. POST a url to /shorten")


@bp.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json(silent=True) or {}
    original_url = data.get("url", "")

    # Only allow real web links
    parsed = urlparse(original_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return jsonify(error="Provide a valid http(s) url"), 400

    conn = get_db_connection()
    try:
        for _ in range(5):  # retry a few times if a code collides
            short_code = generate_short_code()
            try:
                with conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO urls (short_code, original_url) VALUES (%s, %s)",
                            (short_code, original_url),
                        )
                return jsonify(short_url=request.host_url + short_code), 201
            except psycopg2.errors.UniqueViolation:
                continue  # duplicate code, roll back happened, try a new one
        return jsonify(error="Could not generate a unique code"), 500
    finally:
        conn.close()


@bp.route("/<short_code>")
def redirect_to_url(short_code):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT original_url FROM urls WHERE short_code = %s",
                    (short_code,),
                )
                row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return jsonify(error="Short URL not found"), 404
    return redirect(row[0], code=302)
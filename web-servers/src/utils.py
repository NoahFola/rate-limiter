# src/utils.py
import secrets
import string

ALPHABET = string.ascii_letters + string.digits


def generate_short_code(length=6):
    """Return a random code like 'aB3xY9'."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
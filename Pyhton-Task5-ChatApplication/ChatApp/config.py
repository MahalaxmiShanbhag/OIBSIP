"""
config.py
---------
Central configuration for the Flask Chat Application.

Keeping configuration in a single, dedicated module makes it easy to
switch between development / testing / production settings later on
without touching application logic elsewhere in the codebase.
"""

import os

# Base directory of the project (used to build an absolute path to the DB file)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared across all environments."""

    # Secret key used by Flask to sign session cookies.
    # In production, always override this with an environment variable.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-this-in-production")

    # SQLite database stored as a file inside the project root.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )

    # Disable a feature of Flask-SQLAlchemy that adds overhead and is not needed.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-SocketIO async mode. "threading" avoids requiring eventlet/gevent
    # to be perfectly configured, and works well for a moderate number of users.
    SOCKETIO_ASYNC_MODE = "gevent"  # or "threading" if you prefer

    # Session cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

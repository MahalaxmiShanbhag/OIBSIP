"""
utils/auth.py
--------------
Authentication helper functions and decorators.

Keeping this logic separate from app.py keeps routes clean and makes
the authentication rules easy to test / reuse.
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using Werkzeug's secure hashing (PBKDF2)."""
    return generate_password_hash(plain_password)


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Check a plain-text password against a stored hash."""
    return check_password_hash(hashed_password, plain_password)


def login_required(view_func):
    """
    Decorator that protects a route so only logged-in users can access it.
    Redirects to the login page with a flash message otherwise.
    """

    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def validate_registration_input(username: str, password: str, confirm_password: str):
    """
    Validate registration form input.

    Returns a list of error messages (empty list means input is valid).
    """
    errors = []

    if not username or not username.strip():
        errors.append("Username is required.")
    elif len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters long.")
    elif len(username.strip()) > 80:
        errors.append("Username must be under 80 characters.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors

"""Reusable input validation and formatting helpers."""

import re
from datetime import datetime


NUMBER_PATTERN = re.compile(r"^(?:\d+(?:\.\d+)?|\.\d+)$")
NAME_PATTERN = re.compile(r"^[\w\s.'-]+$", re.UNICODE)


def validate_name(value: str) -> str:
    """Validate and normalize a user name."""
    name = value.strip()
    if not name:
        raise ValueError("Please enter a user name.")
    if len(name) > 100 or not NAME_PATTERN.fullmatch(name):
        raise ValueError("User name may contain letters, spaces, apostrophes, periods, and hyphens only.")
    if not any(character.isalpha() for character in name):
        raise ValueError("User name must contain at least one letter.")
    return name


def parse_positive_number(value: str, field_name: str, maximum: float) -> float:
    """Parse a positive decimal value within an inclusive maximum."""
    cleaned = value.strip()
    if not cleaned or not NUMBER_PATTERN.fullmatch(cleaned):
        raise ValueError(f"{field_name} must be a valid positive number.")
    number = float(cleaned)
    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    if number > maximum:
        raise ValueError(f"{field_name} cannot be greater than {maximum:g}.")
    return number


def current_timestamp() -> str:
    """Return a sortable, human-readable timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

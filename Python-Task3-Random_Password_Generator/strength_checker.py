"""
strength_checker.py

Evaluates the strength of a generated password based on its length
and character diversity, returning a label ("Weak", "Medium", "Strong")
and an associated color for GUI display.
"""

import string
from typing import Tuple


class StrengthChecker:
    """Analyzes password strength using length and character diversity."""

    # Colors used by the GUI to visually represent strength.
    WEAK_COLOR = "#e74c3c"      # Red
    MEDIUM_COLOR = "#f39c12"    # Orange
    STRONG_COLOR = "#27ae60"    # Green

    @staticmethod
    def _character_diversity_score(password: str) -> int:
        """
        Count how many distinct character categories are present
        in the password (uppercase, lowercase, digits, symbols).

        Returns:
            int: A score from 0 to 4 representing category diversity.
        """
        score = 0
        if any(ch in string.ascii_uppercase for ch in password):
            score += 1
        if any(ch in string.ascii_lowercase for ch in password):
            score += 1
        if any(ch in string.digits for ch in password):
            score += 1
        if any(ch in string.punctuation for ch in password):
            score += 1
        return score

    @classmethod
    def evaluate(cls, password: str) -> Tuple[str, str]:
        """
        Evaluate the strength of the given password.

        Args:
            password (str): The password to evaluate.

        Returns:
            Tuple[str, str]: (strength_label, color_hex)
        """
        if not password:
            return "N/A", "#7f8c8d"

        length = len(password)
        diversity = cls._character_diversity_score(password)

        # Scoring model combines length weight and diversity weight.
        # Length contributes up to 2 points, diversity up to 4.
        length_score = 0
        if length >= 16:
            length_score = 2
        elif length >= 12:
            length_score = 1

        total_score = length_score + diversity  # Max possible: 6

        if total_score <= 3:
            return "Weak", cls.WEAK_COLOR
        elif total_score <= 5:
            return "Medium", cls.MEDIUM_COLOR
        else:
            return "Strong", cls.STRONG_COLOR

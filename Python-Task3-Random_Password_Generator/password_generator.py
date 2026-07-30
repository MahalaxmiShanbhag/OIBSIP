"""
password_generator.py

Contains the core, cryptographically secure password generation logic.
This module NEVER uses the `random` module — only `secrets`, which is
suitable for generating security-sensitive tokens/passwords.
"""

import string
import secrets
from typing import List


# Characters considered "ambiguous" / easily confused with one another.
AMBIGUOUS_CHARACTERS = "0Oo1lI"


class PasswordGeneratorError(Exception):
    """Custom exception raised for invalid password generation requests."""
    pass


class PasswordGenerator:
    """
    Encapsulates all logic required to build a secure, randomized
    password based on user-selected criteria.
    """

    MIN_LENGTH = 8
    MAX_LENGTH = 64

    def __init__(
        self,
        length: int = 16,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_numbers: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
    ) -> None:
        self.length = length
        self.use_uppercase = use_uppercase
        self.use_lowercase = use_lowercase
        self.use_numbers = use_numbers
        self.use_symbols = use_symbols
        self.exclude_ambiguous = exclude_ambiguous

    def _build_character_pools(self) -> List[str]:
        """
        Build a list of character pools — one pool per selected category.
        Each pool is later used to guarantee at least one character from
        that category appears in the final password.

        Returns:
            List[str]: A list of strings, each representing one
            character category pool (already filtered for ambiguity).
        """
        pools: List[str] = []

        if self.use_uppercase:
            pools.append(self._filter_ambiguous(string.ascii_uppercase))
        if self.use_lowercase:
            pools.append(self._filter_ambiguous(string.ascii_lowercase))
        if self.use_numbers:
            pools.append(self._filter_ambiguous(string.digits))
        if self.use_symbols:
            pools.append(self._filter_ambiguous(string.punctuation))

        # Remove any pool that became empty after ambiguous filtering
        # (this can only happen for the numbers pool in edge cases).
        pools = [pool for pool in pools if pool]

        return pools

    def _filter_ambiguous(self, characters: str) -> str:
        """Remove ambiguous characters from a character set if requested."""
        if not self.exclude_ambiguous:
            return characters
        return "".join(ch for ch in characters if ch not in AMBIGUOUS_CHARACTERS)

    def validate(self) -> None:
        """
        Validate the current configuration.

        Raises:
            PasswordGeneratorError: If the configuration is invalid.
        """
        if not isinstance(self.length, int):
            raise PasswordGeneratorError("Password length must be an integer.")

        if self.length < self.MIN_LENGTH or self.length > self.MAX_LENGTH:
            raise PasswordGeneratorError(
                f"Password length must be between {self.MIN_LENGTH} "
                f"and {self.MAX_LENGTH} characters."
            )

        selected_types = sum(
            [
                self.use_uppercase,
                self.use_lowercase,
                self.use_numbers,
                self.use_symbols,
            ]
        )
        if selected_types < 2:
            raise PasswordGeneratorError(
                "Please select at least two character types."
            )

        pools = self._build_character_pools()
        if len(pools) < 2:
            raise PasswordGeneratorError(
                "Not enough valid characters available after excluding "
                "ambiguous characters. Please adjust your selection."
            )

        if self.length < len(pools):
            raise PasswordGeneratorError(
                "Password length is too short to include at least one "
                "character from every selected category."
            )

    def generate(self) -> str:
        """
        Generate a cryptographically secure password satisfying all
        selected criteria.

        Returns:
            str: The generated password.
        """
        # Validate configuration first; raises PasswordGeneratorError on failure.
        self.validate()

        pools = self._build_character_pools()
        combined_pool = "".join(pools)

        # Step 1: Guarantee at least one character from each selected category.
        password_chars: List[str] = [secrets.choice(pool) for pool in pools]

        # Step 2: Fill the remaining length with secure random choices
        # drawn from the full combined character pool.
        remaining_length = self.length - len(password_chars)
        password_chars.extend(
            secrets.choice(combined_pool) for _ in range(remaining_length)
        )

        # Step 3: Securely shuffle the characters using secrets.
        # (secrets has no shuffle, so we implement a Fisher-Yates shuffle
        # using secrets.randbelow for cryptographically secure randomness.)
        self._secure_shuffle(password_chars)

        return "".join(password_chars)

    @staticmethod
    def _secure_shuffle(items: List[str]) -> None:
        """
        Perform an in-place Fisher-Yates shuffle using `secrets.randbelow`
        for cryptographic security (secrets module has no shuffle helper).

        Args:
            items (List[str]): The list of characters to shuffle in place.
        """
        for i in range(len(items) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            items[i], items[j] = items[j], items[i]

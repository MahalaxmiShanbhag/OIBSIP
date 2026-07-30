"""
history.py

Keeps track of the most recently generated passwords in the current
session only. No data is ever written to disk.
"""

from collections import deque
from typing import Deque, List


class PasswordHistory:
    """
    Maintains a fixed-size, in-memory history of generated passwords.
    Uses collections.deque with maxlen for efficient, automatic
    trimming of the oldest entries.
    """

    def __init__(self, max_size: int = 5) -> None:
        self.max_size = max_size
        # deque automatically discards the oldest item once maxlen is
        # exceeded, giving us a rolling "last N" history for free.
        self._entries: Deque[str] = deque(maxlen=max_size)

    def add(self, password: str) -> None:
        """Add a newly generated password to the history."""
        if password:
            self._entries.appendleft(password)  # newest first

    def get_all(self) -> List[str]:
        """Return the current history as a list, newest first."""
        return list(self._entries)

    def clear(self) -> None:
        """Clear the session history."""
        self._entries.clear()

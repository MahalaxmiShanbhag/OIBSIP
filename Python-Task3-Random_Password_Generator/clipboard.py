"""
clipboard.py

Small wrapper around pyperclip to handle clipboard operations with
proper exception handling, since clipboard access can fail on some
systems (e.g., missing xclip/xsel on Linux).
"""

import pyperclip


class ClipboardError(Exception):
    """Raised when copying to the clipboard fails."""
    pass


def copy_to_clipboard(text: str) -> None:
    """
    Copy the given text to the system clipboard.

    Args:
        text (str): The text to copy.

    Raises:
        ClipboardError: If the clipboard operation fails.
    """
    if not text:
        raise ClipboardError("There is no password to copy.")

    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as exc:
        # pyperclip raises this when no backend (xclip/xsel/pbcopy/etc.)
        # is available on the host system.
        raise ClipboardError(
            "Could not access the system clipboard. Please ensure a "
            "clipboard utility (e.g., xclip or xsel) is installed."
        ) from exc

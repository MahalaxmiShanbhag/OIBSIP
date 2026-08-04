"""
utils/emoji.py
---------------
Converts simple emoji "shortcodes" (e.g. :smile:) typed by users into
their Unicode emoji equivalents before a message is broadcast/stored.
"""

import re

# Mapping of supported shortcodes -> Unicode emoji characters
EMOJI_MAP = {
    ":smile:": "\U0001F604",     # 😄
    ":heart:": "\U00002764\U0000FE0F",  # ❤️
    ":laugh:": "\U0001F602",     # 😂
    ":sad:": "\U0001F622",       # 😢
    ":fire:": "\U0001F525",      # 🔥
    ":thumbsup:": "\U0001F44D",  # 👍
    ":rocket:": "\U0001F680",    # 🚀
}

# Pre-compile a single regex that matches any of the supported shortcodes.
# Sorting by length (longest first) avoids partial-match issues.
_PATTERN = re.compile(
    "|".join(re.escape(code) for code in sorted(EMOJI_MAP, key=len, reverse=True))
)


def convert_emoji_shortcodes(text: str) -> str:
    """
    Replace every recognized :shortcode: in `text` with its Unicode emoji.
    Unrecognized shortcodes are left untouched.
    """
    if not text:
        return text
    return _PATTERN.sub(lambda match: EMOJI_MAP[match.group(0)], text)

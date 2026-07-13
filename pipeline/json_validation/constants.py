"""Schema constants for raw annotated set validation."""

import re

# HTML entities (&amp; &#39; &#x27; etc.) or URL-encoded sequences (%20 etc.)
ENCODED_PATTERN = re.compile(r"&[#\w]+;|%[0-9A-Fa-f]{2}")

VALID_LINE_LABELS = frozenset({"setup", "punchline", "tag", "fluff"})

VALID_JOKE_TYPES = frozenset({
    "misdirect",
    "reframe",
    "phonetic-match",
    "double-meaning",
    "contradiction",
    "analogy",
    "hyperbole",
    "elephant-in-the-room",
    "anti-humor",
})

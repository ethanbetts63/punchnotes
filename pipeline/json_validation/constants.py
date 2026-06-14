"""Schema constants for raw annotated set validation.

These values define the annotation contract only. They intentionally do not
mirror every database field because the import layer can map annotation fields
into older storage names during the current rewrite.
"""

import re

# HTML entities (&amp; &#39; &#x27; etc.) or URL-encoded sequences (%20 etc.)
ENCODED_PATTERN = re.compile(r"&[#\w]+;|%[0-9A-Fa-f]{2}")

VALID_LINE_LABELS = frozenset({"setup", "punchline", "tag", "fluff"})

PREMISE_STRUCTURE_RULES: dict[str, tuple[str, ...]] = {
    "misdirect": ("implies", "but reveals"),
    "reframe": ("could be",),
    "phonetic-match": ("sounds like",),
    "double-meaning": ("can mean", "or"),
    "contradiction": ("both", "and yet"),
    "analogy": ("is like", "because both"),
    "hyperbole": ("becomes so extreme that",),
    "elephant-in-the-room": ("widely understood", "but rarely"),
    "anti-humor": ("implies a punchline, but reveals only",),
}

VALID_JOKE_TYPES = frozenset(PREMISE_STRUCTURE_RULES)

PREMISE_MAX_WORDS = 20

BASE_BEAT_FIELDS = frozenset({"premise", "joke_type"})

JOKE_TYPE_FIELDS: dict[str, tuple[str, ...]] = {
    "misdirect": ("bait", "implication", "reveal"),
    "reframe": ("subject", "reframe"),
    "phonetic-match": ("heard", "reheard"),
    "double-meaning": ("phrase", "expected", "comic"),
    "contradiction": ("subject", "a", "b"),
    "analogy": ("a", "b", "shared"),
    "hyperbole": ("subject", "extreme"),
    "elephant-in-the-room": ("elephant",),
    "anti-humor": ("frame", "answer"),
}

OPTIONAL_JOKE_TYPE_FIELDS: dict[str, tuple[str, ...]] = {
    "phonetic-match": ("reason",),
}

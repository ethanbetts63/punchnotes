import re
from collections import defaultdict

# HTML entities (&amp; &#39; &#x27; etc.) or URL-encoded sequences (%20 etc.)
_ENCODED = re.compile(r"&[#\w]+;|%[0-9A-Fa-f]{2}")

PREMISE_STRUCTURE_RULES: dict[str, tuple[str, ...]] = {
    "misdirect": ("implies", "but"),
    "reframe": ("could be",),
    "phonetic-match": ("sounds like", "and"),
    "double-meaning": ("can mean", "or"),
    "analogy": ("is like", "because both"),
    "hyperbole": ("so", "that"),
    "elephant-in-the-room": ("widely understood", "but rarely"),
}

VALID_JOKE_TYPES = frozenset(PREMISE_STRUCTURE_RULES)


def validate_bit_meta(meta: dict) -> None:
    """Raises ValueError for invalid beat metadata or line-to-beat structure."""
    # Build label list per (bit, beat) from the lines array
    beat_labels: dict[tuple[int, int], list[str]] = defaultdict(list)
    for line in meta.get("lines", []):
        b = line.get("bit")
        bt = line.get("beat")
        if b is not None and bt is not None:
            beat_labels[(int(b), int(bt))].append(line.get("label", ""))

    errors = []

    # Check all line text for encoded characters
    for i, line in enumerate(meta.get("lines", [])):
        text = line.get("text", "")
        match = _ENCODED.search(text)
        if match:
            errors.append(f"line {i + 1}: encoded character {match.group()!r} in text {text!r}")

        label = line.get("label")
        bit = line.get("bit")
        beat = line.get("beat")
        line_ref = line.get("line_number", i + 1)

        if (bit is None) != (beat is None):
            errors.append(
                f"line {line_ref}: bit and beat must both be set or both be null"
            )

        if label != "fluff" and (bit is None or beat is None):
            errors.append(
                f"line {line_ref}: {label!r} lines must have bit and beat values"
            )

    for bit_num, bit_data in meta.get("bit_meta", {}).items():
        beats = bit_data.get("beats", {})
        summary = bit_data.get("summary")
        beat_count = len(beats)
        bit_location = f"bit {bit_num}"

        if beat_count > 1 and (not isinstance(summary, str) or not summary.strip()):
            errors.append(f"{bit_location}: multi-beat bits must have a summary")

        if beat_count <= 1 and summary not in (None, ""):
            errors.append(f"{bit_location}: summary is only allowed on multi-beat bits")

        if "premise" in bit_data:
            errors.append(f"{bit_location}: use summary for multi-beat bits, not premise")

        for beat_num, beat_data in beats.items():
            location = f"bit {bit_num} beat {beat_num}"
            joke_type = beat_data.get("joke_type")
            premise = beat_data.get("premise")

            if joke_type not in PREMISE_STRUCTURE_RULES:
                accepted = ", ".join(sorted(PREMISE_STRUCTURE_RULES))
                errors.append(
                    f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}"
                )
                continue

            if not isinstance(premise, str) or not premise.strip():
                errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
                continue

            match = _ENCODED.search(premise)
            if match:
                errors.append(f"{location}: encoded character {match.group()!r} in premise")

            missing = [
                phrase
                for phrase in PREMISE_STRUCTURE_RULES[joke_type]
                if phrase not in premise.lower()
            ]
            if missing:
                required = ", ".join(f'"{p}"' for p in PREMISE_STRUCTURE_RULES[joke_type])
                errors.append(
                    f"{location}: {joke_type} premise must contain {required}; "
                    f"missing {', '.join(repr(p) for p in missing)}"
                )

            labels = beat_labels.get((int(bit_num), int(beat_num)), [])
            if "punchline" not in labels:
                errors.append(f"{location}: must contain at least 1 punchline line")

    if errors:
        raise ValueError("Invalid bit_meta:\n  " + "\n  ".join(errors))

import re
from collections import defaultdict

# HTML entities (&amp; &#39; &#x27; etc.) or URL-encoded sequences (%20 etc.)
_ENCODED = re.compile(r"&[#\w]+;|%[0-9A-Fa-f]{2}")

VALID_LINE_LABELS = frozenset({"setup", "punchline", "tag", "fluff"})

PREMISE_STRUCTURE_RULES: dict[str, tuple[str, ...]] = {
    "misdirect": ("implies", "but reveals"),
    "reframe": ("could be",),
    "phonetic-match": ("sounds like",),
    "double-meaning": ("can mean", "or"),
    "contradiction": ("both", "and yet"),
    "analogy": ("is like", "because both"),
    "hyperbole": ("taken so far that",),
    "elephant-in-the-room": ("widely understood", "but rarely"),
    "anti-humor": ("implies a punchline, but reveals only",),
}

VALID_JOKE_TYPES = frozenset(PREMISE_STRUCTURE_RULES)

PREMISE_MAX_WORDS = 20

BASE_BEAT_FIELDS = frozenset({"premise", "joke_type", "keys"})

JOKE_TYPE_FIELDS: dict[str, tuple[str, ...]] = {
    "misdirect": ("bait", "implication", "reveal"),
    "reframe": ("subject", "reframe"),
    "phonetic-match": ("heard", "reheard"),
    "double-meaning": ("phrase", "senses"),
    "contradiction": ("subject", "a", "b"),
    "analogy": ("a", "b", "shared"),
    "hyperbole": ("subject", "extreme"),
    "elephant-in-the-room": ("elephant",),
    "anti-humor": ("frame", "answer"),
}

OPTIONAL_JOKE_TYPE_FIELDS: dict[str, tuple[str, ...]] = {
    "phonetic-match": ("reason",),
}

FULL_AUTO_KEY_FIELDS: dict[str, tuple[str, ...]] = {
    "analogy": ("a", "b"),
    "hyperbole": ("subject",),
    "double-meaning": ("phrase",),
}


def _positive_int(value) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _sequential_error(label: str, numbers: set[int]) -> str | None:
    if not numbers:
        return None
    expected = set(range(1, max(numbers) + 1))
    if numbers == expected:
        return None
    missing = ", ".join(str(n) for n in sorted(expected - numbers))
    actual = ", ".join(str(n) for n in sorted(numbers))
    return f"{label}: numbers must be sequential starting at 1; got [{actual}], missing [{missing}]"


def _is_non_empty_string(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _flatten_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _allowed_key_text(joke_type: str, beat_data: dict) -> str:
    fields_by_type = {
        "misdirect": ("bait",),
        "reframe": ("subject", "reframe"),
        "phonetic-match": ("heard", "reason"),
        "double-meaning": ("phrase",),
        "contradiction": ("subject", "a", "b"),
        "analogy": ("a", "b"),
        "hyperbole": ("subject",),
        "elephant-in-the-room": ("elephant",),
        "anti-humor": ("frame",),
    }
    values = []
    for field in fields_by_type.get(joke_type, ()):
        values.extend(_flatten_strings(beat_data.get(field)))
    return " ".join(values).lower()


def _expected_full_auto_keys(joke_type: str, beat_data: dict) -> list[str] | None:
    if joke_type == "phonetic-match":
        expected = [beat_data.get("heard")]
        if _is_non_empty_string(beat_data.get("reason")):
            expected.append(beat_data.get("reason"))
        return [key for key in expected if isinstance(key, str)]

    fields = FULL_AUTO_KEY_FIELDS.get(joke_type)
    if not fields:
        return None
    return [beat_data[field] for field in fields if isinstance(beat_data.get(field), str)]


def validate_bit_meta(meta: dict) -> None:
    """Raises ValueError for invalid raw annotation JSON."""
    errors = []
    punchline_lines: dict[tuple[int, int], list[int]] = defaultdict(list)
    anchor_bits: set[int] = set()
    anchor_beats_by_bit: dict[int, set[int]] = defaultdict(set)

    # Check all line text for encoded characters
    lines = meta.get("lines", [])
    if not isinstance(lines, list):
        raise ValueError("Invalid bit_meta:\n  lines must be a JSON array")

    previous_label = None
    for i, line in enumerate(lines):
        if not isinstance(line, dict):
            errors.append(f"line {i + 1}: line must be a JSON object")
            continue

        text = line.get("text", "")
        match = _ENCODED.search(text)
        if match:
            errors.append(f"line {i + 1}: encoded character {match.group()!r} in text {text!r}")

        label = line.get("label")
        bit = line.get("bit")
        beat = line.get("beat")
        line_ref = line.get("line_number", i + 1)

        if label not in VALID_LINE_LABELS:
            accepted = ", ".join(sorted(VALID_LINE_LABELS))
            errors.append(f"line {line_ref}: label must be one of [{accepted}], got {label!r}")
            previous_label = label
            continue

        if label == "punchline" and (bit is None or beat is None):
            errors.append(
                f"line {line_ref}: {label!r} lines must have bit and beat values"
            )
        elif label == "punchline":
            bit_num = _positive_int(bit)
            beat_num = _positive_int(beat)
            if bit_num is None or beat_num is None:
                errors.append(
                    f"line {line_ref}: punchline bit and beat must be positive integers, "
                    f"got bit={bit!r}, beat={beat!r}"
                )
            else:
                punchline_lines[(bit_num, beat_num)].append(int(line_ref))
                anchor_bits.add(bit_num)
                anchor_beats_by_bit[bit_num].add(beat_num)

        if label != "punchline" and (bit is not None or beat is not None):
            errors.append(
                f"line {line_ref}: {label!r} lines must leave bit and beat null; "
                "the importer infers ownership from punchline anchors"
            )

        if label == "tag" and previous_label not in {"punchline", "tag"}:
            if previous_label is None:
                errors.append(
                    f"line {line_ref}: tag must immediately follow a punchline or tag; "
                    "this is the first line"
                )
            else:
                errors.append(
                    f"line {line_ref}: tag must immediately follow a punchline or tag; "
                    f"previous label is {previous_label!r}"
                )

        previous_label = label

    bit_meta = meta.get("bit_meta", {})
    if not isinstance(bit_meta, dict):
        errors.append("bit_meta must be a JSON object keyed by bit number strings, not an array")
        bit_meta = {}

    meta_beat_keys: set[tuple[int, int]] = set()
    meta_bits: set[int] = set()
    meta_beats_by_bit: dict[int, set[int]] = defaultdict(set)

    for bit_num, bit_data in bit_meta.items():
        parsed_bit_num = _positive_int(bit_num)
        bit_location = f"bit {bit_num}"
        if parsed_bit_num is None:
            errors.append(f"{bit_location}: bit_meta keys must be positive integer strings")
            continue
        meta_bits.add(parsed_bit_num)

        if not isinstance(bit_data, dict):
            errors.append(f"{bit_location}: bit metadata must be a JSON object")
            continue

        beats = bit_data.get("beats", {})
        if not isinstance(beats, dict):
            errors.append(f"{bit_location}: beats must be a JSON object keyed by beat number strings, not an array")
            beats = {}

        summary = bit_data.get("summary")
        beat_count = len(beats)

        if beat_count > 1 and (not isinstance(summary, str) or not summary.strip()):
            errors.append(f"{bit_location}: multi-beat bits must have a summary")

        if beat_count <= 1 and summary not in (None, ""):
            errors.append(f"{bit_location}: summary is only allowed on multi-beat bits")

        if "premise" in bit_data:
            errors.append(f"{bit_location}: use summary for multi-beat bits, not premise")

        for beat_num, beat_data in beats.items():
            parsed_beat_num = _positive_int(beat_num)
            location = f"bit {bit_num} beat {beat_num}"
            if parsed_beat_num is None:
                errors.append(f"{location}: beat keys must be positive integer strings")
                continue
            meta_beat_keys.add((parsed_bit_num, parsed_beat_num))
            meta_beats_by_bit[parsed_bit_num].add(parsed_beat_num)

            if not isinstance(beat_data, dict):
                errors.append(f"{location}: beat metadata must be a JSON object")
                continue

            joke_type = beat_data.get("joke_type")
            premise = beat_data.get("premise")
            keys = beat_data.get("keys")

            if joke_type not in PREMISE_STRUCTURE_RULES:
                accepted = ", ".join(sorted(PREMISE_STRUCTURE_RULES))
                errors.append(
                    f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}"
                )
                continue

            required_fields = JOKE_TYPE_FIELDS[joke_type]
            optional_fields = OPTIONAL_JOKE_TYPE_FIELDS.get(joke_type, ())
            allowed_fields = BASE_BEAT_FIELDS | set(required_fields) | set(optional_fields)
            extra_fields = sorted(set(beat_data) - allowed_fields)
            if extra_fields:
                errors.append(
                    f"{location}: unexpected field(s) for {joke_type}: {', '.join(extra_fields)}"
                )

            for field in required_fields:
                value = beat_data.get(field)
                if field == "senses":
                    if not isinstance(value, list) or len(value) < 2:
                        errors.append(f"{location}: field 'senses' must be an array with at least 2 strings")
                    else:
                        for sense_index, sense in enumerate(value, start=1):
                            if not _is_non_empty_string(sense):
                                errors.append(f"{location}: senses item {sense_index} must be a non-empty string")
                elif not _is_non_empty_string(value):
                    errors.append(f"{location}: field {field!r} is required for joke_type {joke_type!r}")

            for field in optional_fields:
                value = beat_data.get(field)
                if value is not None and not _is_non_empty_string(value):
                    errors.append(f"{location}: optional field {field!r} must be a non-empty string when present")

            if not isinstance(premise, str) or not premise.strip():
                errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
                continue

            match = _ENCODED.search(premise)
            if match:
                errors.append(f"{location}: encoded character {match.group()!r} in premise")

            word_count = len(premise.split())
            if word_count > PREMISE_MAX_WORDS:
                errors.append(
                    f"{location}: premise is {word_count} words (max {PREMISE_MAX_WORDS}); "
                    f"condense without losing the comedic mechanism: {premise!r}"
                )

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

            if joke_type == "phonetic-match":
                has_reason = _is_non_empty_string(beat_data.get("reason"))
                has_fits_because = "fits because" in premise.lower()
                if has_reason and not has_fits_because:
                    errors.append(
                        f"{location}: phonetic-match premise with reason must contain 'fits because'"
                    )
                if not has_reason and has_fits_because:
                    errors.append(
                        f"{location}: phonetic-match premise contains 'fits because' but has no reason field"
                    )

            if not isinstance(keys, list):
                errors.append(f"{location}: keys must be a JSON array of 1-4 short strings")
            elif not 1 <= len(keys) <= 4:
                errors.append(f"{location}: keys must contain 1-4 items, got {len(keys)}")
            else:
                expected_keys = _expected_full_auto_keys(joke_type, beat_data)
                if expected_keys is not None and keys != expected_keys:
                    errors.append(
                        f"{location}: keys for {joke_type} must be copied from premise fields "
                        f"as {expected_keys!r}, got {keys!r}"
                    )

                allowed_key_text = _allowed_key_text(joke_type, beat_data)
                for key_index, key in enumerate(keys, start=1):
                    if not isinstance(key, str) or not key.strip():
                        errors.append(f"{location}: key {key_index} must be a non-empty string")
                    elif len(key.split()) > 4:
                        errors.append(f"{location}: key {key_index} is too long; use a short searchable noun phrase")
                    elif expected_keys is None and key.lower() not in allowed_key_text:
                        errors.append(
                            f"{location}: key {key_index} {key!r} must come from allowed "
                            f"{joke_type} premise field(s), not transcript-only wording"
                        )

            if (parsed_bit_num, parsed_beat_num) not in punchline_lines:
                errors.append(f"{location}: must contain at least 1 punchline line")

    bit_sequence_error = _sequential_error("bit_meta", meta_bits | anchor_bits)
    if bit_sequence_error:
        errors.append(bit_sequence_error)

    for bit_num in sorted(set(meta_beats_by_bit) | set(anchor_beats_by_bit)):
        beat_sequence_error = _sequential_error(
            f"bit {bit_num} beats",
            meta_beats_by_bit[bit_num] | anchor_beats_by_bit[bit_num],
        )
        if beat_sequence_error:
            errors.append(beat_sequence_error)

    for bit_num, beat_num in sorted(punchline_lines):
        if (bit_num, beat_num) not in meta_beat_keys:
            line_list = ", ".join(str(n) for n in punchline_lines[(bit_num, beat_num)])
            errors.append(
                f"line(s) {line_list}: punchline references bit {bit_num} beat {beat_num}, "
                "but bit_meta has no matching beat"
            )

    if errors:
        raise ValueError("Invalid bit_meta:\n  " + "\n  ".join(errors))

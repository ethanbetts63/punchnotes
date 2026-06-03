"""Beat metadata validation for premises, fields, and optional keys.

This validator enforces joke-type-specific premise structure and field shape.
When a beat provides `keys`, it validates those keys against the premise fields;
it does not require `keys`.
"""

from collections import defaultdict

from .constants import (
    BASE_BEAT_FIELDS,
    ENCODED_PATTERN,
    FULL_AUTO_KEY_FIELDS,
    JOKE_TYPE_FIELDS,
    OPTIONAL_JOKE_TYPE_FIELDS,
    PREMISE_MAX_WORDS,
    PREMISE_STRUCTURE_RULES,
)
from .utils import flatten_strings, is_non_empty_string, positive_int


class BeatMetaValidation:
    def __init__(self, bit_meta: dict, punchline_lines: dict[tuple[int, int], list[int]]):
        self.bit_meta = bit_meta
        self.punchline_lines = punchline_lines
        self.errors: list[str] = []
        self.meta_beat_keys: set[tuple[int, int]] = set()
        self.meta_bits: set[int] = set()
        self.meta_beats_by_bit: dict[int, set[int]] = defaultdict(set)

    def run(self) -> "BeatMetaValidation":
        for bit_num, bit_data in self.bit_meta.items():
            self._validate_bit(bit_num, bit_data)
        self._validate_punchline_metadata_links()
        return self

    def _validate_bit(self, bit_num, bit_data) -> None:
        parsed_bit_num = positive_int(bit_num)
        bit_location = f"bit {bit_num}"
        if parsed_bit_num is None:
            self.errors.append(f"{bit_location}: bit_meta keys must be positive integer strings")
            return
        self.meta_bits.add(parsed_bit_num)

        if not isinstance(bit_data, dict):
            self.errors.append(f"{bit_location}: bit metadata must be a JSON object")
            return

        beats = bit_data.get("beats", {})
        if not isinstance(beats, dict):
            self.errors.append(f"{bit_location}: beats must be a JSON object keyed by beat number strings, not an array")
            beats = {}

        self._validate_bit_summary(bit_location, bit_data, len(beats))

        for beat_num, beat_data in beats.items():
            self._validate_beat(parsed_bit_num, bit_num, beat_num, beat_data)

    def _validate_bit_summary(self, bit_location: str, bit_data: dict, beat_count: int) -> None:
        summary = bit_data.get("summary")
        if beat_count > 1 and (not isinstance(summary, str) or not summary.strip()):
            self.errors.append(f"{bit_location}: multi-beat bits must have a summary")

        if beat_count <= 1 and summary not in (None, ""):
            self.errors.append(f"{bit_location}: summary is only allowed on multi-beat bits")

        if "premise" in bit_data:
            self.errors.append(f"{bit_location}: use summary for multi-beat bits, not premise")

    def _validate_beat(self, parsed_bit_num: int, bit_num, beat_num, beat_data) -> None:
        parsed_beat_num = positive_int(beat_num)
        location = f"bit {bit_num} beat {beat_num}"
        if parsed_beat_num is None:
            self.errors.append(f"{location}: beat keys must be positive integer strings")
            return

        self.meta_beat_keys.add((parsed_bit_num, parsed_beat_num))
        self.meta_beats_by_bit[parsed_bit_num].add(parsed_beat_num)

        if not isinstance(beat_data, dict):
            self.errors.append(f"{location}: beat metadata must be a JSON object")
            return

        joke_type = beat_data.get("joke_type")
        if joke_type not in PREMISE_STRUCTURE_RULES:
            accepted = ", ".join(sorted(PREMISE_STRUCTURE_RULES))
            self.errors.append(f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}")
            return

        self._validate_fields(location, joke_type, beat_data)
        self._validate_premise(location, joke_type, beat_data)
        self._validate_keys(location, joke_type, beat_data)

        if (parsed_bit_num, parsed_beat_num) not in self.punchline_lines:
            self.errors.append(f"{location}: must contain at least 1 punchline line")

    def _validate_fields(self, location: str, joke_type: str, beat_data: dict) -> None:
        required_fields = JOKE_TYPE_FIELDS[joke_type]
        optional_fields = OPTIONAL_JOKE_TYPE_FIELDS.get(joke_type, ())
        allowed_fields = BASE_BEAT_FIELDS | set(required_fields) | set(optional_fields)

        extra_fields = sorted(set(beat_data) - allowed_fields)
        if extra_fields:
            self.errors.append(f"{location}: unexpected field(s) for {joke_type}: {', '.join(extra_fields)}")

        for field in required_fields:
            value = beat_data.get(field)
            if not is_non_empty_string(value):
                self.errors.append(f"{location}: field {field!r} is required for joke_type {joke_type!r}")

        for field in optional_fields:
            value = beat_data.get(field)
            if value is not None and not is_non_empty_string(value):
                self.errors.append(f"{location}: optional field {field!r} must be a non-empty string when present")

    def _validate_premise(self, location: str, joke_type: str, beat_data: dict) -> None:
        premise = beat_data.get("premise")
        if not isinstance(premise, str) or not premise.strip():
            self.errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
            return

        match = ENCODED_PATTERN.search(premise)
        if match:
            self.errors.append(f"{location}: encoded character {match.group()!r} in premise")

        word_count = len(premise.split())
        if word_count > PREMISE_MAX_WORDS:
            self.errors.append(
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
            self.errors.append(
                f"{location}: {joke_type} premise must contain {required}; "
                f"missing {', '.join(repr(p) for p in missing)}"
            )

        if joke_type == "phonetic-match":
            self._validate_phonetic_reason(location, beat_data, premise)

    def _validate_phonetic_reason(self, location: str, beat_data: dict, premise: str) -> None:
        has_reason = is_non_empty_string(beat_data.get("reason"))
        has_fits_because = "fits because" in premise.lower()
        if has_reason and not has_fits_because:
            self.errors.append(f"{location}: phonetic-match premise with reason must contain 'fits because'")
        if not has_reason and has_fits_because:
            self.errors.append(f"{location}: phonetic-match premise contains 'fits because' but has no reason field")

    def _validate_keys(self, location: str, joke_type: str, beat_data: dict) -> None:
        if "keys" not in beat_data:
            return

        keys = beat_data.get("keys")
        if not isinstance(keys, list):
            self.errors.append(f"{location}: keys must be a JSON array of 1-4 short strings")
            return

        if not 1 <= len(keys) <= 4:
            self.errors.append(f"{location}: keys must contain 1-4 items, got {len(keys)}")
            return

        expected_keys = self._expected_full_auto_keys(joke_type, beat_data)
        if expected_keys is not None and keys != expected_keys:
            self.errors.append(
                f"{location}: keys for {joke_type} must be copied from premise fields "
                f"as {expected_keys!r}, got {keys!r}"
            )

        allowed_key_text = self._allowed_key_text(joke_type, beat_data)
        for key_index, key in enumerate(keys, start=1):
            if not isinstance(key, str) or not key.strip():
                self.errors.append(f"{location}: key {key_index} must be a non-empty string")
            elif joke_type != "double-meaning" and len(key.split()) > 4:
                self.errors.append(f"{location}: key {key_index} is too long; use a short searchable noun phrase")
            elif expected_keys is None and key.lower() not in allowed_key_text:
                self.errors.append(
                    f"{location}: key {key_index} {key!r} must come from allowed "
                    f"{joke_type} premise field(s), not transcript-only wording"
                )

    def _allowed_key_text(self, joke_type: str, beat_data: dict) -> str:
        fields_by_type = {
            "misdirect": ("bait", "implication", "reveal"),
            "reframe": ("subject", "reframe"),
            "phonetic-match": ("heard", "reheard", "reason"),
            "double-meaning": ("phrase", "comic"),
            "contradiction": ("subject", "a", "b"),
            "analogy": ("a", "b", "shared"),
            "hyperbole": ("subject", "extreme"),
            "elephant-in-the-room": ("elephant",),
            "anti-humor": ("frame",),
        }
        values = []
        for field in fields_by_type.get(joke_type, ()):
            values.extend(flatten_strings(beat_data.get(field)))
        return " ".join(values).lower()

    def _expected_full_auto_keys(self, joke_type: str, beat_data: dict) -> list[str] | None:
        if joke_type == "phonetic-match":
            expected = [beat_data.get("heard"), beat_data.get("reheard")]
            if is_non_empty_string(beat_data.get("reason")):
                expected.append(beat_data.get("reason"))
            return [key for key in expected if isinstance(key, str)]

        if joke_type == "analogy":
            expected = [beat_data.get("a"), beat_data.get("b")]
            shared_key = self._analogy_shared_key(beat_data.get("shared"))
            if shared_key:
                expected.append(shared_key)
            return [key for key in expected if isinstance(key, str)]

        if joke_type == "hyperbole":
            expected = []
            subject = self._strip_leading_article(beat_data.get("subject"))
            if subject:
                expected.append(subject)
            extreme = beat_data.get("extreme")
            if is_non_empty_string(extreme):
                expected.append(extreme)
            return expected

        fields = FULL_AUTO_KEY_FIELDS.get(joke_type)
        if not fields:
            return None
        return [beat_data[field] for field in fields if isinstance(beat_data.get(field), str)]

    def _analogy_shared_key(self, shared) -> str | None:
        if not is_non_empty_string(shared):
            return None

        key = shared.strip()
        for helper in ("involve ", "involves ", "are ", "is ", "could ", "would ", "can ", "might "):
            if key.lower().startswith(helper):
                return key[len(helper):].strip()
        return key

    def _strip_leading_article(self, value) -> str | None:
        if not is_non_empty_string(value):
            return None

        key = value.strip()
        for article in ("a ", "an ", "the "):
            if key.lower().startswith(article):
                return key[len(article):].strip()
        return key

    def _validate_punchline_metadata_links(self) -> None:
        for bit_num, beat_num in sorted(self.punchline_lines):
            if (bit_num, beat_num) not in self.meta_beat_keys:
                line_list = ", ".join(str(n) for n in self.punchline_lines[(bit_num, beat_num)])
                self.errors.append(
                    f"line(s) {line_list}: punchline references bit {bit_num} beat {beat_num}, "
                    "but bit_meta has no matching beat"
                )

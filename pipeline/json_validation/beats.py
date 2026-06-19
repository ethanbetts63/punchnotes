"""Beat metadata validation for premises and joke-type-specific fields."""

from collections import defaultdict

from pipeline.json_validation.constants import (
    BASE_BEAT_FIELDS,
    ENCODED_PATTERN,
    JOKE_TYPE_FIELDS,
    OPTIONAL_JOKE_TYPE_FIELDS,
    PREMISE_MAX_WORDS,
    PREMISE_STRUCTURE_RULES,
)
from pipeline.json_validation.utils import is_non_empty_string, positive_int


class BeatMetaValidation:
    def __init__(
        self,
        bit_meta: dict,
        punchline_lines: dict[tuple[int, int], list[int]],
        single_line_premises: dict[tuple[int, int], str] | None = None,
    ):
        self.bit_meta = bit_meta
        self.punchline_lines = punchline_lines
        self.single_line_premises = single_line_premises or {}
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

        self._validate_no_bit_level_premise(bit_location, bit_data)

        for beat_num, beat_data in beats.items():
            self._validate_beat(parsed_bit_num, bit_num, beat_num, beat_data)

    def _validate_no_bit_level_premise(self, bit_location: str, bit_data: dict) -> None:
        if "premise" in bit_data:
            self.errors.append(f"{bit_location}: premise belongs on each beat, not on the bit")

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
        self._validate_premise(location, parsed_bit_num, parsed_beat_num, joke_type, beat_data)

        if (parsed_bit_num, parsed_beat_num) not in self.punchline_lines:
            self.errors.append(f"{location}: must contain at least 1 punchline line")

    def _validate_fields(self, location: str, joke_type: str, beat_data: dict) -> None:
        required_fields = JOKE_TYPE_FIELDS[joke_type]
        optional_fields = OPTIONAL_JOKE_TYPE_FIELDS.get(joke_type, ())
        allowed_fields = BASE_BEAT_FIELDS | set(required_fields) | set(optional_fields)

        extra_fields = sorted(set(beat_data) - allowed_fields - {"keys"})
        if extra_fields:
            self.errors.append(f"{location}: unexpected field(s) for {joke_type}: {', '.join(extra_fields)}")

        if not any(f in beat_data for f in required_fields):
            return

        for field in required_fields:
            value = beat_data.get(field)
            if not is_non_empty_string(value):
                self.errors.append(f"{location}: field {field!r} is required for joke_type {joke_type!r}")

        for field in optional_fields:
            value = beat_data.get(field)
            if value is not None and not is_non_empty_string(value):
                self.errors.append(f"{location}: optional field {field!r} must be a non-empty string when present")

    def _validate_premise(
        self,
        location: str,
        bit_num: int,
        beat_num: int,
        joke_type: str,
        beat_data: dict,
    ) -> None:
        premise = beat_data.get("premise")
        if not isinstance(premise, str) or not premise.strip():
            self.errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
            return

        match = ENCODED_PATTERN.search(premise)
        if match:
            self.errors.append(f"{location}: encoded character {match.group()!r} in premise")

        if premise == self.single_line_premises.get((bit_num, beat_num)):
            return

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

        if joke_type == "phonetic-match" and any(f in beat_data for f in JOKE_TYPE_FIELDS[joke_type]):
            self._validate_phonetic_reason(location, beat_data, premise)

    def _validate_phonetic_reason(self, location: str, beat_data: dict, premise: str) -> None:
        has_reason = is_non_empty_string(beat_data.get("reason"))
        has_fits_because = "fits because" in premise.lower()
        if has_reason and not has_fits_because:
            self.errors.append(f"{location}: phonetic-match premise with reason must contain 'fits because'")
        if not has_reason and has_fits_because:
            self.errors.append(f"{location}: phonetic-match premise contains 'fits because' but has no reason field")

    def _validate_punchline_metadata_links(self) -> None:
        for bit_num, beat_num in sorted(self.punchline_lines):
            if (bit_num, beat_num) not in self.meta_beat_keys:
                line_list = ", ".join(str(n) for n in self.punchline_lines[(bit_num, beat_num)])
                self.errors.append(
                    f"line(s) {line_list}: punchline references bit {bit_num} beat {beat_num}, "
                    "but bit_meta has no matching beat"
                )

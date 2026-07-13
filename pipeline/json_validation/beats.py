"""Beat metadata validation for bit/beat structure and flat joke types."""

from collections import defaultdict

from pipeline.json_validation.constants import VALID_JOKE_TYPES
from pipeline.json_validation.utils import positive_int


class BeatMetaValidation:
    def __init__(
        self,
        bit_meta: dict,
        punchline_lines: dict[tuple[int, int], list[int]],
    ):
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

        for beat_num, beat_data in beats.items():
            self._validate_beat(parsed_bit_num, bit_num, beat_num, beat_data)

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
        if joke_type not in VALID_JOKE_TYPES:
            accepted = ", ".join(sorted(VALID_JOKE_TYPES))
            self.errors.append(f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}")
            return

        if (parsed_bit_num, parsed_beat_num) not in self.punchline_lines:
            self.errors.append(f"{location}: must contain at least 1 punchline line")

    def _validate_punchline_metadata_links(self) -> None:
        for bit_num, beat_num in sorted(self.punchline_lines):
            if (bit_num, beat_num) not in self.meta_beat_keys:
                line_list = ", ".join(str(n) for n in self.punchline_lines[(bit_num, beat_num)])
                self.errors.append(
                    f"line(s) {line_list}: punchline references bit {bit_num} beat {beat_num}, "
                    "but bit_meta has no matching beat"
                )

"""Line-level validation for raw annotation files.

This validator checks labels, punchline anchors, tag adjacency, encoded text,
and the raw-output rule that only punchlines carry explicit bit/beat numbers.
It also records the punchline anchors used later by beat metadata validation.
"""

from collections import defaultdict

from pipeline.json_validation.constants import ENCODED_PATTERN, VALID_LINE_LABELS
from pipeline.json_validation.utils import positive_int


class LineValidation:
    def __init__(self, lines: list):
        self.lines = lines
        self.errors: list[str] = []
        self.punchline_lines: dict[tuple[int, int], list[int]] = defaultdict(list)
        self.anchor_bits: set[int] = set()
        self.anchor_beats_by_bit: dict[int, set[int]] = defaultdict(set)

    def run(self) -> "LineValidation":
        previous_label = None
        seen_punchline = False
        for i, line in enumerate(self.lines):
            if not isinstance(line, dict):
                self.errors.append(f"line {i + 1}: line must be a JSON object")
                continue

            self._validate_line(i, line, previous_label, seen_punchline)
            previous_label = line.get("label")
            if previous_label == "punchline":
                seen_punchline = True
        self._validate_single_punchline_per_beat()
        return self

    def _validate_line(self, index: int, line: dict, previous_label: str | None, seen_punchline: bool) -> None:
        text = line.get("text", "")
        match = ENCODED_PATTERN.search(text)
        if match:
            self.errors.append(f"line {index + 1}: encoded character {match.group()!r} in text {text!r}")

        label = line.get("label")
        bit = line.get("bit")
        beat = line.get("beat")
        line_ref = line.get("line_number", index + 1)

        if label not in VALID_LINE_LABELS:
            accepted = ", ".join(sorted(VALID_LINE_LABELS))
            self.errors.append(f"line {line_ref}: label must be one of [{accepted}], got {label!r}")
            return

        if label == "punchline":
            self._validate_punchline_anchor(line_ref, bit, beat)
        elif bit is not None or beat is not None:
            self.errors.append(
                f"line {line_ref}: {label!r} lines must leave bit and beat null; "
                "the importer infers ownership from punchline anchors"
            )

        if label == "tag":
            if not seen_punchline:
                self.errors.append(
                    f"line {line_ref}: tag must ride a preceding punchline; "
                    "no punchline appears before this line"
                )
            elif previous_label not in {"punchline", "tag", "setup"}:
                self.errors.append(
                    f"line {line_ref}: tag must follow a punchline, tag, or its own setup; "
                    f"previous label is {previous_label!r}"
                )

    def _validate_punchline_anchor(self, line_ref, bit, beat) -> None:
        if bit is None or beat is None:
            self.errors.append(f"line {line_ref}: 'punchline' lines must have bit and beat values")
            return

        bit_num = positive_int(bit)
        beat_num = positive_int(beat)
        if bit_num is None or beat_num is None:
            self.errors.append(
                f"line {line_ref}: punchline bit and beat must be positive integers, "
                f"got bit={bit!r}, beat={beat!r}"
            )
            return

        line_num = int(line_ref)
        self.punchline_lines[(bit_num, beat_num)].append(line_num)
        self.anchor_bits.add(bit_num)
        self.anchor_beats_by_bit[bit_num].add(beat_num)

    def _validate_single_punchline_per_beat(self) -> None:
        line_index_by_number = {
            int(line.get("line_number", i + 1)): i
            for i, line in enumerate(self.lines)
            if isinstance(line, dict)
        }

        for (bit_num, beat_num), line_numbers in sorted(self.punchline_lines.items()):
            if len(line_numbers) <= 1:
                continue

            indexes = [line_index_by_number[line_number] for line_number in line_numbers]
            if indexes == list(range(min(indexes), max(indexes) + 1)):
                continue

            line_list = ", ".join(str(line_number) for line_number in line_numbers)
            self.errors.append(
                f"bit {bit_num} beat {beat_num}: multiple punchline lines ({line_list}) "
                "are only allowed when they are consecutive transcript-split lines"
            )

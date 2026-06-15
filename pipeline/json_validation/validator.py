"""Top-level coordinator for raw annotated set validation.

The public `validate_bit_meta` function runs line validation first, then beat
metadata validation, and finally cross-checks sequential bit/beat numbering.
It raises one ValueError containing all discovered issues so annotators get
precise feedback in a single import attempt.
"""

from pipeline.json_validation.premises import populate_single_line_punchline_premises
from pipeline.json_validation.beats import BeatMetaValidation
from pipeline.json_validation.lines import LineValidation
from pipeline.json_validation.utils import sequential_error


def validate_bit_meta(meta: dict) -> None:
    """Raises ValueError for invalid raw annotation JSON."""
    errors = []

    lines = meta.get("lines", [])
    if not isinstance(lines, list):
        raise ValueError("Invalid bit_meta:\n  lines must be a JSON array")

    line_validation = LineValidation(lines).run()
    errors.extend(line_validation.errors)

    single_line_premises = populate_single_line_punchline_premises(meta)

    bit_meta = meta.get("bit_meta", {})
    if not isinstance(bit_meta, dict):
        errors.append("bit_meta must be a JSON object keyed by bit number strings, not an array")
        bit_meta = {}

    beat_validation = BeatMetaValidation(
        bit_meta,
        line_validation.punchline_lines,
        single_line_premises=single_line_premises,
    ).run()
    errors.extend(beat_validation.errors)

    bit_sequence_error = sequential_error(
        "bit_meta",
        beat_validation.meta_bits | line_validation.anchor_bits,
    )
    if bit_sequence_error:
        errors.append(bit_sequence_error)

    beat_bit_nums = set(beat_validation.meta_beats_by_bit) | set(line_validation.anchor_beats_by_bit)
    for bit_num in sorted(beat_bit_nums):
        beat_sequence_error = sequential_error(
            f"bit {bit_num} beats",
            beat_validation.meta_beats_by_bit[bit_num] | line_validation.anchor_beats_by_bit[bit_num],
        )
        if beat_sequence_error:
            errors.append(beat_sequence_error)

    if errors:
        raise ValueError("Invalid bit_meta:\n  " + "\n  ".join(errors))

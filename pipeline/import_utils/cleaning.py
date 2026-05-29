from collections import defaultdict
from copy import deepcopy


def clean_fluff_bit_beat(meta: dict) -> dict:
    """Assign bit/beat ownership to fluff lines based on surrounding joke lines."""
    cleaned = deepcopy(meta)

    bit_spans: dict[int, list[int]] = defaultdict(list)
    beat_spans: dict[tuple[int, int], list[int]] = defaultdict(list)

    for line in cleaned.get("lines", []):
        if line.get("label") == "fluff":
            continue

        bit = line.get("bit")
        beat = line.get("beat")
        if bit is None or beat is None:
            continue

        bit_num = int(bit)
        beat_num = int(beat)
        line_number = int(line.get("line_number", 0))
        bit_spans[bit_num].append(line_number)
        beat_spans[(bit_num, beat_num)].append(line_number)

    for line in cleaned.get("lines", []):
        if line.get("label") != "fluff":
            continue

        line_number = int(line.get("line_number", 0))
        line["bit"] = None
        line["beat"] = None

        for bit_num, line_numbers in bit_spans.items():
            if min(line_numbers) < line_number < max(line_numbers):
                line["bit"] = bit_num
                break

        if line["bit"] is None:
            continue

        for (bit_num, beat_num), line_numbers in beat_spans.items():
            if bit_num == line["bit"] and min(line_numbers) < line_number < max(line_numbers):
                line["beat"] = beat_num
                break

    return cleaned

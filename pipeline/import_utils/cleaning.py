from collections import defaultdict
from copy import deepcopy


def clean_fluff_bit_beat(meta: dict) -> dict:
    """Assign line ownership from punchline anchors and surrounding joke spans."""
    cleaned = deepcopy(meta)
    lines = cleaned.get("lines", [])

    next_punchline = None
    for line in reversed(lines):
        if line.get("label") == "punchline" and line.get("bit") is not None and line.get("beat") is not None:
            next_punchline = (int(line["bit"]), int(line["beat"]))

        if line.get("label") == "setup" and (line.get("bit") is None or line.get("beat") is None):
            if next_punchline is not None:
                line["bit"], line["beat"] = next_punchline

    previous_payoff = None
    for line in lines:
        label = line.get("label")
        if label == "punchline" and line.get("bit") is not None and line.get("beat") is not None:
            previous_payoff = (int(line["bit"]), int(line["beat"]))
            continue

        if label == "tag":
            if line.get("bit") is None or line.get("beat") is None:
                if previous_payoff is not None:
                    line["bit"], line["beat"] = previous_payoff
            if line.get("bit") is not None and line.get("beat") is not None:
                previous_payoff = (int(line["bit"]), int(line["beat"]))

    bit_spans: dict[int, list[int]] = defaultdict(list)
    beat_spans: dict[tuple[int, int], list[int]] = defaultdict(list)

    for line in lines:
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

    for line in lines:
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

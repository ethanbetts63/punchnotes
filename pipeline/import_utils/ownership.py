from collections import defaultdict


def infer_line_ownership(lines_data: list) -> dict[int, tuple[int | None, int | None]]:
    """Infer DB line ownership from punchline anchors without mutating raw data."""
    ownership: dict[int, tuple[int | None, int | None]] = {}
    next_punchline = None

    for line in reversed(lines_data):
        line_number = int(line["line_number"])
        if line.get("label") == "punchline" and line.get("bit") is not None and line.get("beat") is not None:
            next_punchline = (int(line["bit"]), int(line["beat"]))
            ownership[line_number] = next_punchline
            continue

        if line.get("label") == "setup" and next_punchline is not None:
            ownership[line_number] = next_punchline
        else:
            ownership[line_number] = (None, None)

    previous_payoff = None
    for line in lines_data:
        line_number = int(line["line_number"])
        label = line.get("label")
        bit, beat = ownership[line_number]

        if label == "punchline" and bit is not None and beat is not None:
            previous_payoff = (bit, beat)
            continue

        if label == "tag" and previous_payoff is not None:
            ownership[line_number] = previous_payoff
            previous_payoff = previous_payoff

    bit_spans: dict[int, list[int]] = defaultdict(list)
    beat_spans: dict[tuple[int, int], list[int]] = defaultdict(list)
    for line in lines_data:
        if line.get("label") == "fluff":
            continue

        line_number = int(line["line_number"])
        bit, beat = ownership[line_number]
        if bit is None or beat is None:
            continue
        bit_spans[bit].append(line_number)
        beat_spans[(bit, beat)].append(line_number)

    for line in lines_data:
        if line.get("label") != "fluff":
            continue

        line_number = int(line["line_number"])
        inferred_bit = None
        inferred_beat = None

        for bit_num, line_numbers in bit_spans.items():
            if min(line_numbers) < line_number < max(line_numbers):
                inferred_bit = bit_num
                break

        if inferred_bit is not None:
            for (bit_num, beat_num), line_numbers in beat_spans.items():
                if bit_num == inferred_bit and min(line_numbers) < line_number < max(line_numbers):
                    inferred_beat = beat_num
                    break

        ownership[line_number] = (inferred_bit, inferred_beat)

    return ownership

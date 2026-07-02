from collections import defaultdict


def infer_line_ownership(lines_data: list) -> dict[int, tuple[int | None, int | None]]:
    """Infer DB line ownership from punchline anchors without mutating raw data.

    Payoff lines carry beat identity: a punchline owns its explicit (bit, beat)
    anchor, and a tag inherits the most recent payoff's beat. A setup joins the
    beat of the *next* payoff line — so a setup followed by a tag stays in the
    current beat, while a setup followed by a punchline opens the new one.
    """
    ownership: dict[int, tuple[int | None, int | None]] = {}

    # Punchlines own themselves from their explicit anchors.
    for line in lines_data:
        line_number = int(line["line_number"])
        if line.get("label") == "punchline" and line.get("bit") is not None and line.get("beat") is not None:
            ownership[line_number] = (int(line["bit"]), int(line["beat"]))

    # Tags inherit the most recent payoff's beat (walking forward).
    previous_payoff = None
    for line in lines_data:
        line_number = int(line["line_number"])
        label = line.get("label")
        if label == "punchline" and line_number in ownership:
            previous_payoff = ownership[line_number]
        elif label == "tag" and previous_payoff is not None:
            ownership[line_number] = previous_payoff

    # Setups join the next payoff's beat (walking backward past other setups).
    next_payoff = None
    for line in reversed(lines_data):
        line_number = int(line["line_number"])
        label = line.get("label")
        if label in {"punchline", "tag"} and line_number in ownership:
            next_payoff = ownership[line_number]
        elif label == "setup":
            ownership[line_number] = next_payoff if next_payoff is not None else (None, None)

    # Orphan tags/setups and every fluff line default to null before span fill.
    for line in lines_data:
        ownership.setdefault(int(line["line_number"]), (None, None))

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

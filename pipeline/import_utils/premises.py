from collections import defaultdict

from .ownership import infer_line_ownership


def infer_single_line_punchline_premises(lines_data: list) -> dict[tuple[int, int], str]:
    """Return fallback premises when a beat's only non-fluff line is the punchline."""
    ownership = infer_line_ownership(lines_data)
    beat_lines: dict[tuple[int, int], list[dict]] = defaultdict(list)

    for line in lines_data:
        bit, beat = ownership[int(line["line_number"])]
        if bit is None or beat is None:
            continue
        beat_lines[(bit, beat)].append(line)

    fallback_premises: dict[tuple[int, int], str] = {}
    for beat_key, owned_lines in beat_lines.items():
        non_fluff_lines = [line for line in owned_lines if line.get("label") != "fluff"]
        if len(non_fluff_lines) != 1:
            continue
        owned_line = non_fluff_lines[0]
        if owned_line.get("label") != "punchline":
            continue
        text = owned_line.get("text")
        if isinstance(text, str) and text.strip():
            fallback_premises[beat_key] = text.strip()

    return fallback_premises


def populate_single_line_punchline_premises(meta: dict) -> dict[tuple[int, int], str]:
    """Mutate eligible beats to use their punchline text as the stored premise."""
    lines_data = meta.get("lines", [])
    bit_meta = meta.get("bit_meta", {})
    if not isinstance(lines_data, list) or not isinstance(bit_meta, dict):
        return {}

    fallback_premises = infer_single_line_punchline_premises(lines_data)
    for bit_num_str, bit_data in bit_meta.items():
        if not isinstance(bit_data, dict):
            continue
        beats = bit_data.get("beats", {})
        if not isinstance(beats, dict):
            continue

        try:
            bit_num = int(bit_num_str)
        except (TypeError, ValueError):
            continue

        for beat_num_str, beat_data in beats.items():
            if not isinstance(beat_data, dict):
                continue
            try:
                beat_num = int(beat_num_str)
            except (TypeError, ValueError):
                continue

            fallback = fallback_premises.get((bit_num, beat_num))
            if fallback:
                beat_data["premise"] = fallback

    return fallback_premises

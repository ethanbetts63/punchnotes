from pipeline.models import Beat, Line


def load_lines_by_set(beats: list) -> dict:
    set_ids = {beat.bit.set_id for beat in beats}
    if not set_ids:
        return {}

    lines_by_set = {}
    lines = (
        Line.objects
        .filter(set_id__in=set_ids, label__in=("setup", "punchline"))
        .order_by("set_id", "line_number")
        .values_list("set_id", "line_number", "label", "text")
    )
    for set_id, line_number, label, text in lines:
        lines_by_set.setdefault(set_id, []).append((line_number, label, text))
    return lines_by_set


def embedding_text(beat: Beat, lines_by_set: dict | None = None, text_format: str = "plain") -> str | None:
    if lines_by_set is None:
        lines = (
            Line.objects
            .filter(
                set_id=beat.bit.set_id,
                label__in=("setup", "punchline"),
                line_number__gte=beat.line_start,
                line_number__lte=beat.line_end,
            )
            .order_by("line_number")
            .values_list("label", "text")
        )
    else:
        lines = (
            (label, text)
            for line_number, label, text in lines_by_set.get(beat.bit.set_id, [])
            if beat.line_start <= line_number <= beat.line_end
        )

    setup_parts = []
    punchline_parts = []
    for label, text in lines:
        if label == "setup":
            setup_parts.append(text)
        else:
            punchline_parts.append(text)

    if not punchline_parts:
        return None

    setup_text = " ".join(setup_parts).strip()
    punchline_text = " ".join(punchline_parts).strip()

    if text_format == "structured":
        parts = []
        if setup_text:
            parts.append(f"Setup: {setup_text}")
        parts.append(f"Punchline: {punchline_text}")
        return "\n".join(parts)

    parts = []
    if setup_text:
        parts.append(setup_text)
    parts.append(punchline_text)
    return " ".join(parts)

SEARCHABLE_BEAT_LINE_LABELS = ("setup", "punchline", "tag")


def build_beat_search_text(lines_data: list, line_numbers: set) -> str:
    """Join a beat's setup/punchline/tag line text (fluff excluded) in line order.

    Matching against this joined text (instead of one Line row at a time) lets a
    search phrase that was split across adjacent transcript lines still match.
    """
    texts = [
        line["text"]
        for line in lines_data
        if int(line["line_number"]) in line_numbers and line.get("label") in SEARCHABLE_BEAT_LINE_LABELS
    ]
    return " ".join(texts)

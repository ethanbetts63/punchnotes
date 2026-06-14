SEARCHABLE_BEAT_LINE_LABELS = ("setup", "punchline", "tag")


def beat_lines(beat, set_lines=None):
    lines = set_lines if set_lines is not None else beat.bit.set.lines.all()
    return [
        line
        for line in lines
        if beat.line_start <= line.line_number <= beat.line_end
    ]


def describe_beat_lines(beat, query="", set_lines=None):
    lines = beat_lines(beat, set_lines=set_lines)
    setup_lines = []
    punchline = ""
    matched_line = None
    query_lower = query.lower()

    for line in lines:
        if line.label == "setup":
            setup_lines.append(line.text)
        elif line.label == "punchline" and not punchline:
            punchline = line.text

        if (
            query
            and matched_line is None
            and line.label in SEARCHABLE_BEAT_LINE_LABELS
            and query_lower in line.text.lower()
        ):
            matched_line = line

    return {
        "lines": lines,
        "setup_lines": setup_lines,
        "punchline": punchline,
        "matched_line": matched_line,
    }

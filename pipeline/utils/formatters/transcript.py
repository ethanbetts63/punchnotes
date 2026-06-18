from pipeline.utils.formatters.json import compact_lines, dump_object


TRANSCRIPT_LINE_FIELD_ORDER = ["line_number", "text", "start", "duration"]


def serialize_transcript(data: dict) -> str:
    return dump_object(data.items(), {
        "lines": compact_lines(TRANSCRIPT_LINE_FIELD_ORDER),
    })

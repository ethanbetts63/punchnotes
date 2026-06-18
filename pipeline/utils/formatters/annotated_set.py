import json

from pipeline.utils.formatters.json import compact_lines, dump_object, reorder


SET_FIELD_ORDER = [
    "type", "video_id", "comedian_name",
    "start_seconds", "interview_end_line", "interview_end_seconds",
    "set_attributes", "comedian_attributes", "bit_meta", "lines",
]

LINE_FIELD_ORDER = ["text", "label", "bit", "beat", "line_number", "start"]

BEAT_FIELD_ORDER = [
    "premise", "joke_type",
    "bait", "implication", "reveal",
    "subject", "reframe", "extreme",
    "heard", "reheard", "reason",
    "phrase", "expected", "comic",
    "a", "b", "shared",
    "elephant", "frame", "answer",
]


def format_nested_metadata(obj, depth):
    if not obj:
        return "{}"

    pad = "  " * depth
    inner = "  " * (depth + 1)
    if any(key in obj for key in BEAT_FIELD_ORDER):
        obj = reorder(obj, BEAT_FIELD_ORDER)

    rows = []
    items = list(obj.items())
    for index, (key, value) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        if isinstance(value, dict):
            formatted = format_nested_metadata(value, depth + 1)
        else:
            formatted = json.dumps(value, ensure_ascii=False)
        rows.append(f"{inner}{json.dumps(key)}: {formatted}{comma}")
    return "{\n" + "\n".join(rows) + "\n" + pad + "}"


def serialize_annotated_set(data: dict) -> str:
    out = {}
    for key in SET_FIELD_ORDER:
        if key == "set_attributes":
            out[key] = list(data.get("set_attributes") or [])
        elif key == "comedian_attributes":
            out[key] = list(data.get("comedian_attributes") or [])
        elif key in {"interview_end_line", "interview_end_seconds"}:
            out[key] = data.get(key)
        elif key in data:
            out[key] = data[key]

    for key, value in data.items():
        if key not in out:
            out[key] = value

    return dump_object(out.items(), {
        "bit_meta": lambda value: format_nested_metadata(value, depth=1),
        "lines": compact_lines(LINE_FIELD_ORDER),
    })

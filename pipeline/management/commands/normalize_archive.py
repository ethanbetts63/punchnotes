import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


SET_FIELD_ORDER = [
    "type", "video_id", "episode_title", "episode_url", "publish_date",
    "guests", "comedian_name", "comedian_type", "set_number",
    "start_seconds", "interview_end_line", "interview_end_seconds",
    "joke_book", "comedian_attributes", "bit_meta", "lines",
]

LINE_FIELD_ORDER = ["text", "label", "bit", "beat", "line_number", "start"]

TRANSCRIPT_LINE_FIELD_ORDER = ["line_number", "text", "start", "duration"]

BEAT_FIELD_ORDER = ["premise", "joke_type", "topics"]

JOKE_BOOK_VALUES = {"small", "medium", "large"}


def _reorder(d, order):
    """Return d with keys in order first, then any remainder."""
    out = {k: d[k] for k in order if k in d}
    out.update({k: v for k, v in d.items() if k not in out})
    return out


def _normalize_joke_book(value):
    """Canonicalize joke book size, leaving uncertain values as null."""
    if value is None:
        return None

    if not isinstance(value, str):
        return None

    text = value.strip().lower()
    if not text or text in {"null", "none", "unknown", "unclear"}:
        return None

    if text in JOKE_BOOK_VALUES:
        return text

    normalized = text.replace("-", " ")
    if "medium" in normalized:
        return "medium"
    if any(word in normalized.split() for word in ["small", "little", "smallest"]):
        return "small"
    if any(word in normalized.split() for word in ["big", "large"]):
        return "large"

    return None


def _fmt_nested(obj, depth):
    """Recursively serialize a dict with 2-space indent; all lists compact.
    Applies BEAT_FIELD_ORDER to leaf dicts that look like beat objects."""
    if not obj:
        return "{}"
    pad = "  " * depth
    inner = "  " * (depth + 1)
    # Apply beat field ordering if this dict has beat-like keys
    if any(k in obj for k in BEAT_FIELD_ORDER):
        obj = _reorder(obj, BEAT_FIELD_ORDER)
    rows = []
    items = list(obj.items())
    for i, (k, v) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        if isinstance(v, dict):
            val = _fmt_nested(v, depth + 1)
        else:
            val = json.dumps(v, ensure_ascii=False)
        rows.append(f"{inner}{json.dumps(k)}: {val}{comma}")
    return "{\n" + "\n".join(rows) + "\n" + pad + "}"


def serialize_set(data: dict) -> str:
    """
    Canonical format:
      - Top-level fields in FIELD_ORDER, 2-space indented
      - 'guests': compact array on one line
      - 'interview_end_line': always present (null if absent), after 'start_seconds'
      - 'interview_end_seconds': always present (null if absent), after 'interview_end_line'
      - 'joke_book': always present (null if absent), after interview metadata
      - 'bit_meta': expanded structure, but all arrays (topics etc.) compact
      - 'lines': each element a compact single-line object
    """
    # Build ordered output dict; nullable metadata fields are inserted even if absent.
    out = {}
    for key in SET_FIELD_ORDER:
        if key == "joke_book":
            out[key] = _normalize_joke_book(data.get("joke_book"))  # null if absent or uncertain
        elif key in {"interview_end_line", "interview_end_seconds"}:
            out[key] = data.get(key)
        elif key in data:
            out[key] = data[key]
    # Preserve any unrecognised keys at the end
    for key, val in data.items():
        if key not in out:
            out[key] = val

    rows = ["{\n"]
    items = list(out.items())
    for i, (key, value) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""

        if key == "guests":
            val_str = json.dumps(value, ensure_ascii=False)

        elif key == "bit_meta":
            val_str = _fmt_nested(value, depth=1)

        elif key == "lines":
            inner = []
            for j, ln in enumerate(value):
                lcomma = "," if j < len(value) - 1 else ""
                ln = _reorder(ln, LINE_FIELD_ORDER)
                inner.append(f"    {json.dumps(ln, ensure_ascii=False)}{lcomma}")
            val_str = "[\n" + "\n".join(inner) + "\n  ]"

        else:
            val_str = json.dumps(value, ensure_ascii=False)

        rows.append(f"  {json.dumps(key)}: {val_str}{comma}\n")

    rows.append("}\n")
    return "".join(rows)


def serialize_transcript(data: dict) -> str:
    """
    Canonical transcript format:
      - Top-level fields 2-space indented
      - 'lines': each transcript line is a compact single-line object
    """
    rows = ["{\n"]
    items = list(data.items())
    for i, (key, value) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""

        if key == "lines":
            inner = []
            for j, ln in enumerate(value):
                lcomma = "," if j < len(value) - 1 else ""
                ln = _reorder(ln, TRANSCRIPT_LINE_FIELD_ORDER)
                inner.append(f"    {json.dumps(ln, ensure_ascii=False)}{lcomma}")
            val_str = "[\n" + "\n".join(inner) + "\n  ]"
        else:
            val_str = json.dumps(value, ensure_ascii=False)

        rows.append(f"  {json.dumps(key)}: {val_str}{comma}\n")

    rows.append("}\n")
    return "".join(rows)


def normalize_path(path, serializer):
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    new = serializer(data)
    if new == raw.replace("\r\n", "\n"):
        return False

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    return True


class Command(BaseCommand):
    help = "Normalize JSON formatting of archived annotated sets and transcripts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sets-path",
            type=Path,
            help="Directory of annotated set JSON files to normalize.",
        )
        parser.add_argument(
            "--transcripts-path",
            type=Path,
            help="Directory of transcript JSON files to normalize.",
        )

    def handle(self, *args, **options):
        sets_path = options.get("sets_path")
        transcripts_path = options.get("transcripts_path")
        if sets_path or transcripts_path:
            archives = []
            if sets_path:
                archives.append(("bit annotated sets", sets_path, serialize_set))
            if transcripts_path:
                archives.append(("transcripts", transcripts_path, serialize_transcript))
        else:
            archives = [
                (
                    "bit annotated sets",
                    settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive",
                    serialize_set,
                ),
                (
                    "transcripts",
                    settings.PIPELINE_DATA_DIR / "transcript_archive",
                    serialize_transcript,
                ),
            ]

        total_changed = 0
        total_paths = 0
        for label, archive, serializer in archives:
            paths = sorted(archive.glob("*.json"))
            changed = sum(1 for path in paths if normalize_path(path, serializer))
            total_changed += changed
            total_paths += len(paths)
            self.stdout.write(f"Normalized {changed}/{len(paths)} {label}.")

        if not total_paths:
            self.stdout.write("No files found.")
            return

        self.stdout.write(self.style.SUCCESS(f"Normalized {total_changed}/{total_paths} files."))

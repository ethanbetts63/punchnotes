import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

SET_FIELD_ORDER = [
    "type", "video_id", "episode_title", "episode_url", "publish_date",
    "guests", "comedian_name",
    "start_seconds", "interview_end_line", "interview_end_seconds",
    "set_attributes", "comedian_attributes", "bit_meta", "lines",
]

LINE_FIELD_ORDER = ["text", "label", "bit", "beat", "line_number", "start"]

TRANSCRIPT_LINE_FIELD_ORDER = ["line_number", "text", "start", "duration"]

BEAT_FIELD_ORDER = [
    "premise", "joke_type",
    "bait", "implication", "reveal",
    "subject", "reframe", "extreme",
    "heard", "reheard", "reason",
    "phrase", "expected", "comic",
    "a", "b", "shared",
    "elephant", "frame", "answer",
]

def _reorder(d, order):
    """Return d with keys in order first, then any remainder."""
    out = {k: d[k] for k in order if k in d}
    out.update({k: v for k, v in d.items() if k not in out})
    return out


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


def _compact_lines(field_order):
    def fmt(lines):
        inner = []
        for j, ln in enumerate(lines):
            lcomma = "," if j < len(lines) - 1 else ""
            inner.append(f"    {json.dumps(_reorder(ln, field_order), ensure_ascii=False)}{lcomma}")
        return "[\n" + "\n".join(inner) + "\n  ]"
    return fmt


def _dump_object(items, handlers=None):
    default = lambda v: json.dumps(v, ensure_ascii=False)
    handlers = handlers or {}
    rows = ["{\n"]
    entries = list(items)
    for i, (key, value) in enumerate(entries):
        comma = "," if i < len(entries) - 1 else ""
        rows.append(f"  {json.dumps(key)}: {handlers.get(key, default)(value)}{comma}\n")
    rows.append("}\n")
    return "".join(rows)


def serialize_set(data: dict) -> str:
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
    for key, val in data.items():
        if key not in out:
            out[key] = val
    return _dump_object(out.items(), {
        "bit_meta": lambda v: _fmt_nested(v, depth=1),
        "lines": _compact_lines(LINE_FIELD_ORDER),
    })


def serialize_transcript(data: dict) -> str:
    return _dump_object(data.items(), {
        "lines": _compact_lines(TRANSCRIPT_LINE_FIELD_ORDER),
    })


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

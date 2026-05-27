import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


FIELD_ORDER = [
    "type", "video_id", "episode_title", "episode_url", "publish_date",
    "guests", "comedian_name", "comedian_type", "set_number",
    "start_seconds", "joke_book", "bit_meta", "lines",
]


def _fmt_nested(obj, depth):
    """Recursively serialize a dict with 2-space indent; all lists compact."""
    if not obj:
        return "{}"
    pad = "  " * depth
    inner = "  " * (depth + 1)
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


def serialize(data: dict) -> str:
    """
    Canonical format:
      - Top-level fields in FIELD_ORDER, 2-space indented
      - 'guests': compact array on one line
      - 'joke_book': always present (null if absent), after 'start_seconds'
      - 'bit_meta': expanded structure, but all arrays (topics etc.) compact
      - 'lines': each element a compact single-line object
    """
    # Build ordered output dict; joke_book inserted after start_seconds even if absent
    out = {}
    for key in FIELD_ORDER:
        if key == "joke_book":
            out[key] = data.get("joke_book")  # null if not in source
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
                inner.append(f"    {json.dumps(ln, ensure_ascii=False)}{lcomma}")
            val_str = "[\n" + "\n".join(inner) + "\n  ]"

        else:
            val_str = json.dumps(value, ensure_ascii=False)

        rows.append(f"  {json.dumps(key)}: {val_str}{comma}\n")

    rows.append("}\n")
    return "".join(rows)


class Command(BaseCommand):
    help = "Normalize JSON formatting of all files in data/bit_annotated_set_archive/"

    def handle(self, *args, **options):
        archive = settings.BASE_DIR / "data" / "bit_annotated_set_archive"
        paths = sorted(archive.glob("*.json"))
        if not paths:
            self.stdout.write("No files found.")
            return

        changed = 0
        for path in paths:
            raw = path.read_text(encoding="utf-8-sig")
            data = json.loads(raw)
            new = serialize(data)
            if new != raw.replace("\r\n", "\n"):
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)
                changed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Normalized {changed}/{len(paths)} files.")
        )

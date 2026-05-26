import json

from django.conf import settings
from django.core.management.base import BaseCommand

LINE_FIELD_ORDER = ["text", "label", "bit", "beat", "line_number", "start"]


def format_line(line):
    ordered = {k: line[k] for k in LINE_FIELD_ORDER if k in line}
    ordered.update({k: v for k, v in line.items() if k not in LINE_FIELD_ORDER})
    return json.dumps(ordered, ensure_ascii=False)


def serialize(obj, depth=0):
    """Serialize obj with indentation, collapsing compact values to one line."""
    pad = "  " * depth
    inner = "  " * (depth + 1)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        items = list(obj.items())
        serialized = [(k, serialize(v, depth + 1)) for k, v in items]
        if len(serialized) == 1:
            (k0, v0), (_, v0_str) = items[0], serialized[0]
            if not isinstance(v0, dict) and "\n" not in v0_str:
                inline = "{" + f"{json.dumps(k0)}: {v0_str}" + "}"
                if len(inline) <= 120:
                    return inline
        lines = ["{"]
        for i, (k, v_str) in enumerate(serialized):
            comma = "," if i < len(serialized) - 1 else ""
            lines.append(f"{inner}{json.dumps(k)}: {v_str}{comma}")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        if all(not isinstance(item, (dict, list)) for item in obj):
            return json.dumps(obj, ensure_ascii=False)
        lines = ["["]
        for i, item in enumerate(obj):
            comma = "," if i < len(obj) - 1 else ""
            lines.append(f"{inner}{serialize(item, depth + 1)}{comma}")
        lines.append(f"{pad}]")
        return "\n".join(lines)
    else:
        return json.dumps(obj, ensure_ascii=False)


def dump(data):
    non_lines = [(k, v) for k, v in data.items() if k != "lines"]
    parts = ["{"]
    for i, (k, v) in enumerate(non_lines):
        parts.append(f"  {json.dumps(k)}: {serialize(v, depth=1)},")
    parts.append('  "lines": [')
    lines = data["lines"]
    for i, line in enumerate(lines):
        comma = "," if i < len(lines) - 1 else ""
        parts.append(f"    {format_line(line)}{comma}")
    parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


class Command(BaseCommand):
    help = "Reformat archive files: compact one-line-per-line with field order text, label, bit, beat, ..."

    def handle(self, *args, **options):
        archive = settings.BASE_DIR / "data" / "bit_annotated_set_archive"
        files = sorted(archive.glob("*.json"))

        if not files:
            self.stdout.write("No files found.")
            return

        for path in files:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            path.write_text(dump(data), encoding="utf-8")
            self.stdout.write(f"  {path.name}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. {len(files)} files reformatted."))

import json

from django.conf import settings
from django.core.management.base import BaseCommand

LINE_FIELD_ORDER = ["text", "label", "bit", "beat", "line_number", "start"]


def format_line(line):
    ordered = {k: line[k] for k in LINE_FIELD_ORDER if k in line}
    ordered.update({k: v for k, v in line.items() if k not in LINE_FIELD_ORDER})
    return json.dumps(ordered, ensure_ascii=False)


def indent_value(v_str):
    lines = v_str.split("\n")
    return lines[0] + "\n" + "\n".join("  " + l for l in lines[1:])


def dump(data):
    non_lines = [(k, v) for k, v in data.items() if k != "lines"]
    parts = ["{"]
    for i, (k, v) in enumerate(non_lines):
        v_str = indent_value(json.dumps(v, ensure_ascii=False, indent=2))
        parts.append(f"  {json.dumps(k)}: {v_str},")
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

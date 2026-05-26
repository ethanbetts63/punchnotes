import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def extract_trailing_number(id_string):
    match = re.search(r"(\d+)$", id_string)
    return int(match.group(1)) if match else None


def convert(data):
    bit_meta = {}
    line_map = {}  # line_number -> (bit_num, beat_num)

    for bit in data.get("bits", []):
        bit_num = extract_trailing_number(bit["bit_id"])
        beats_meta = {}
        for beat in bit.get("beats", []):
            beat_num = extract_trailing_number(beat["beat_id"])
            beats_meta[str(beat_num)] = {"topics": beat.get("topics", [])}
            start, end = beat["line_range"]
            for line in data["lines"]:
                ln = line["line_number"]
                if start <= ln <= end:
                    line_map[ln] = (bit_num, beat_num)
        bit_meta[str(bit_num)] = {
            "premise": bit["premise"],
            "beats": beats_meta,
        }

    new_lines = []
    for line in data["lines"]:
        ln = line["line_number"]
        assignment = line_map.get(ln)
        new_lines.append({
            "line_number": ln,
            "text": line["text"],
            "start": line["start"],
            "label": line["label"],
            "bit": assignment[0] if assignment else None,
            "beat": assignment[1] if assignment else None,
        })

    new_doc = {k: v for k, v in data.items() if k not in ("bits", "lines")}
    if bit_meta:
        new_doc["bit_meta"] = bit_meta
    new_doc["lines"] = new_lines
    return new_doc


class Command(BaseCommand):
    help = "Migrate bit_annotated_set_archive files from nested bits/beats to flat bit/beat fields on each line"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be changed without writing anything",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        archive = settings.BASE_DIR / "data" / "bit_annotated_set_archive"
        files = sorted(archive.glob("*.json"))

        if not files:
            self.stdout.write("No files found in bit_annotated_set_archive.")
            return

        for path in files:
            data = json.loads(path.read_text(encoding="utf-8-sig"))

            if "bits" not in data:
                self.stdout.write(f"  {path.name}: already migrated, skipping")
                continue

            new_data = convert(data)

            if dry_run:
                self.stdout.write(f"  {path.name}: would migrate ({len(new_data['lines'])} lines, {len(new_data.get('bit_meta', {}))} bits)")
            else:
                path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding="utf-8")
                self.stdout.write(self.style.SUCCESS(
                    f"  {path.name}: migrated ({len(new_data['lines'])} lines, {len(new_data.get('bit_meta', {}))} bits)"
                ))

        if dry_run:
            self.stdout.write("\nDry run — no files written.")
        else:
            self.stdout.write(self.style.SUCCESS(f"\nDone. {len(files)} files processed."))

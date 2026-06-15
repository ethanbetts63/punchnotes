import json
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.management.commands.extract_set import dump_set, WHISPER_ANNOTATION_RE


class Command(BaseCommand):
    help = "Strip Whisper annotation lines (e.g. [laughter], [music]) from bit_annotated_set_archive files."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print what would change without writing files")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        archive_dir = settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive"
        files = sorted(archive_dir.glob("*.json"))

        total_removed = 0
        files_changed = 0

        for path in files:
            doc = json.loads(path.read_text(encoding="utf-8"))
            lines = doc.get("lines", [])
            cleaned = [line for line in lines if not WHISPER_ANNOTATION_RE.match(line.get("text", ""))]
            removed = len(lines) - len(cleaned)

            if removed == 0:
                continue

            total_removed += removed
            files_changed += 1
            self.stdout.write(f"{path.name}: removed {removed} line(s)")

            if not dry_run:
                doc["lines"] = cleaned
                path.write_text(dump_set(doc), encoding="utf-8")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDry run — {total_removed} line(s) across {files_changed} file(s) would be removed."))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nDone — removed {total_removed} line(s) across {files_changed} file(s)."))

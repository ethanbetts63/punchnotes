import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.management.commands.normalize_archive import serialize_set


class Command(BaseCommand):
    help = "Temporarily remove top-level set_number fields from pipeline set JSON files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report files that would change without writing them.",
        )
        parser.add_argument(
            "--path",
            action="append",
            type=Path,
            help="Directory to scan. Can be supplied multiple times; defaults to the active set inboxes and archive.",
        )

    def handle(self, *args, **options):
        if options["path"]:
            directories = options["path"]
        else:
            directories = [
                settings.PIPELINE_DATA_DIR / "2_set_inbox",
                settings.PIPELINE_DATA_DIR / "4_bit_annotated_set_inbox",
                settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive",
            ]

        total_files = 0
        changed = 0
        dry_run = options["dry_run"]

        for directory in directories:
            if not directory.exists():
                self.stdout.write(self.style.WARNING(f"Skipping missing directory: {directory}"))
                continue

            for path in sorted(directory.glob("*.json")):
                total_files += 1
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                if "set_number" not in data:
                    continue

                changed += 1
                if dry_run:
                    self.stdout.write(f"Would remove set_number from {path}")
                    continue

                data.pop("set_number", None)
                path.write_text(serialize_set(data), encoding="utf-8", newline="\n")
                self.stdout.write(f"Removed set_number from {path}")

        action = "Would update" if dry_run else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} {changed}/{total_files} JSON file(s)."))

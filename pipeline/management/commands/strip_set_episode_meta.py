import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.management.commands.normalize_archive import serialize_set


REMOVE_KEYS = {"episode_title", "episode_url", "publish_date", "guests"}
TARGET_DIR_NAMES = ("bit_annotated_set_archive", "2_set_inbox")


class Command(BaseCommand):
    help = "Temporary cleanup: strip episode metadata fields from set JSON files."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true", help="Report changes without rewriting files.")
        parser.add_argument("--no-backup", action="store_true", help="Do not create a .bak file before rewriting.")

    def handle(self, *args, **options):
        changed = failed = scanned = 0
        targets = [settings.PIPELINE_DATA_DIR / name for name in TARGET_DIR_NAMES]

        for directory in targets:
            if not directory.exists():
                continue
            for path in sorted(directory.glob("*.json")):
                scanned += 1
                try:
                    data = json.loads(path.read_text(encoding="utf-8-sig"))
                except Exception as exc:
                    failed += 1
                    self.stdout.write(self.style.ERROR(f"{path}: {exc}"))
                    continue

                cleaned = {key: value for key, value in data.items() if key not in REMOVE_KEYS}
                if cleaned == data:
                    continue

                changed += 1
                if options["check"]:
                    continue

                if not options["no_backup"]:
                    backup_path = Path(str(path) + ".bak")
                    if not backup_path.exists():
                        shutil.copy2(path, backup_path)
                path.write_text(serialize_set(cleaned), encoding="utf-8", newline="\n")

        action = "would change" if options["check"] else "changed"
        self.stdout.write(self.style.SUCCESS(f"{scanned} scanned, {changed} {action}, {failed} failed."))

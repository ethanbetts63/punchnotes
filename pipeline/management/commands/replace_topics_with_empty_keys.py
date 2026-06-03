import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.management.commands.normalize_archive import serialize_set


def replace_topics_with_empty_keys(data: dict) -> int:
    """Replace beat-level topics fields with empty keys arrays."""
    changed = 0
    bit_meta = data.get("bit_meta")
    if not isinstance(bit_meta, dict):
        return changed

    for bit_data in bit_meta.values():
        if not isinstance(bit_data, dict):
            continue

        beats = bit_data.get("beats")
        if not isinstance(beats, dict):
            continue

        for beat_data in beats.values():
            if not isinstance(beat_data, dict) or "topics" not in beat_data:
                continue

            beat_data.pop("topics", None)
            beat_data["keys"] = []
            changed += 1

    return changed


def process_path(path: Path, dry_run: bool = False) -> int:
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    changed = replace_topics_with_empty_keys(data)
    if not changed or dry_run:
        return changed

    new = serialize_set(data)
    path.write_text(new, encoding="utf-8", newline="\n")
    return changed


class Command(BaseCommand):
    help = "Replace archived beat-level topics fields with empty keys arrays."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sets-path",
            type=Path,
            default=settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive",
            help="Directory of archived annotated set JSON files to update.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report changes without writing files.",
        )

    def handle(self, *args, **options):
        sets_path = options["sets_path"]
        dry_run = options["dry_run"]
        paths = sorted(sets_path.glob("*.json"))

        total_beats = 0
        changed_files = 0
        for path in paths:
            changed_beats = process_path(path, dry_run=dry_run)
            if changed_beats:
                changed_files += 1
                total_beats += changed_beats

        action = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {total_beats} beat(s) across {changed_files}/{len(paths)} file(s)."
            )
        )

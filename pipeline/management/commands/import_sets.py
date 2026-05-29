import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Comedian
from pipeline.import_utils.validation import validate_bit_meta
from pipeline.import_utils.records import (
    import_bits,
    import_lines,
    refresh_episode_counts,
    upsert_comedian,
    upsert_episode,
    upsert_set,
)


class Command(BaseCommand):
    help = "Import bit-annotated set JSON files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            dest="source_dir",
            default=None,
            help=(
                "Directory to read JSON files from. "
                "Defaults to pipeline/data/4_bit_annotated_set_inbox/ and moves processed files to the archive. "
                "When --dir is supplied the files are read in place and not moved."
            ),
        )

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR

        if options["source_dir"]:
            source = Path(options["source_dir"])
            archive = None  # don't move files when reading from a custom dir
        else:
            source = data_dir / "4_bit_annotated_set_inbox"
            archive = data_dir / "bit_annotated_set_archive"
            archive.mkdir(parents=True, exist_ok=True)

        files = sorted(source.glob("*.json"))
        if not files:
            self.stdout.write(f"No JSON files found in {source}")
            return

        self.stdout.write(f"Importing {len(files)} file(s) from {source}...")

        for path in files:
            try:
                self._import(path)
                if archive:
                    shutil.move(str(path), archive / path.name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {path.name}: {e}"))

    def _import(self, path):
        match = re.match(r"^(.+)_set(\d+)_(.+)$", path.stem)
        if not match:
            raise ValueError(f"Filename does not match expected pattern: {path.name}")

        video_id = match.group(1)
        set_number = int(match.group(2))
        slug = match.group(3)

        meta = json.loads(path.read_text(encoding="utf-8-sig"))
        validate_bit_meta(meta)

        episode = upsert_episode(video_id, meta)
        comedian = upsert_comedian(slug, meta)
        set_obj = upsert_set(episode, set_number, comedian, meta)

        for guest_name in meta.get("guests", []):
            guest_slug = re.sub(r"[^a-z0-9]+", "-", guest_name.lower()).strip("-")
            guest, _ = Comedian.objects.get_or_create(
                slug=guest_slug,
                defaults={"name": guest_name},
            )
            episode.guests.add(guest)

        lines = import_lines(set_obj, meta["lines"])
        import_bits(set_obj, meta["lines"], meta.get("bit_meta", {}))
        refresh_episode_counts(episode)

        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_number:02d} {meta['comedian_name']}: "
                f"{len(lines)} lines, {len(meta.get('bit_meta', {}))} bits"
            )
        )

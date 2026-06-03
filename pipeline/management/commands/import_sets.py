import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from pipeline.models import Comedian
from pipeline.import_utils.comedian_aliases import canonicalize_comedian_name, load_relationships
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
                "Defaults to pipeline/data/3_bit_annotated_set_inbox/ and moves processed files to the archive. "
                "When --dir is supplied the files are read in place and not moved."
            ),
        )

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR

        if options["source_dir"]:
            source = Path(options["source_dir"])
            archive = None  # don't move files when reading from a custom dir
        else:
            source = data_dir / "3_bit_annotated_set_inbox"
            archive = data_dir / "bit_annotated_set_archive"
            archive.mkdir(parents=True, exist_ok=True)

        files = sorted(source.glob("*.json"))
        if not files:
            self.stdout.write(f"No JSON files found in {source}")
            return

        self.stdout.write(f"Importing {len(files)} file(s) from {source}...")
        relationships = load_relationships()

        for path in files:
            try:
                self._import(path, relationships)
                if archive:
                    shutil.move(str(path), archive / path.name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {path.name}: {e}"))

        self.stdout.write("\nFinding similar comedian names...")
        call_command("find_similar_comedians", stdout=self.stdout)

    def _import(self, path, relationships):
        meta = json.loads(path.read_text(encoding="utf-8-sig"))
        validate_bit_meta(meta)

        video_id = meta["video_id"]
        canonical_comedian = canonicalize_comedian_name(meta["comedian_name"], relationships)
        meta = {
            **meta,
            "comedian_name": canonical_comedian.name,
        }

        episode = upsert_episode(video_id, meta)
        comedian = upsert_comedian(canonical_comedian.slug, meta)
        with transaction.atomic():
            set_obj = upsert_set(episode, comedian, meta)

            for guest_name in meta.get("guests", []):
                canonical_guest = canonicalize_comedian_name(guest_name, relationships)
                guest, _ = Comedian.objects.get_or_create(
                    slug=canonical_guest.slug,
                    defaults={"name": canonical_guest.name},
                )
                episode.guests.add(guest)

            lines = import_lines(set_obj, meta["lines"])
            import_bits(set_obj, meta["lines"], meta.get("bit_meta", {}))
            refresh_episode_counts(episode)

        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_obj.set_number:02d} {meta['comedian_name']}: "
                f"{len(lines)} lines, {len(meta.get('bit_meta', {}))} bits"
            )
        )

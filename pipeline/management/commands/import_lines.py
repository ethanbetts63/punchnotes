import json
import re
import shutil

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
    help = "Import bit-annotated set JSON files from data/4_bit_annotated_set_inbox/"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        inbox = data_dir / "4_bit_annotated_set_inbox"
        archive = data_dir / "bit_annotated_set_archive"
        archive.mkdir(exist_ok=True)

        files = sorted(inbox.glob("*.json"))
        if not files:
            self.stdout.write("No files in 4_bit_annotated_set_inbox.")
            return

        for path in files:
            try:
                self._import(path)
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

import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat, Comedian, Episode, Set


class Command(BaseCommand):
    help = "Import beat JSONL files from data/beat_inbox/ into the database"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        beat_inbox = data_dir / "beat_inbox"
        set_inbox = data_dir / "set_inbox"
        processed_beats = data_dir / "processed_beats"

        beat_files = sorted(beat_inbox.glob("*_beats.jsonl"))
        if not beat_files:
            self.stdout.write("No beat files found in beat_inbox.")
            return

        for beat_path in beat_files:
            try:
                self._import(beat_path, set_inbox)
                shutil.move(str(beat_path), processed_beats / beat_path.name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {beat_path.name}: {e}"))

    def _import(self, beat_path, set_inbox):
        # Filename: {video_id}_set{NN}_{slug}_beats.jsonl
        match = re.match(r"^(.+)_(set\d+)_(.+)_beats$", beat_path.stem)
        if not match:
            raise ValueError(f"Filename does not match expected pattern: {beat_path.name}")

        video_id = match.group(1)
        set_tag = match.group(2)          # e.g. "set13"
        slug = match.group(3)             # e.g. "matt-worldly"
        set_number = int(set_tag[3:])     # strip "set" prefix

        # Read set_meta from the corresponding set file
        set_file = set_inbox / f"{video_id}_{set_tag}_{slug}.jsonl"
        if not set_file.exists():
            raise FileNotFoundError(f"Set file not found: {set_file}")

        meta = json.loads(set_file.read_text(encoding="utf-8").splitlines()[0])

        # get_or_create Episode
        episode, _ = Episode.objects.get_or_create(
            video_id=video_id,
            defaults={
                "episode_title": meta["episode_title"],
                "episode_url": meta["episode_url"],
            },
        )

        # get_or_create Comedian
        comedian, _ = Comedian.objects.get_or_create(
            slug=slug,
            defaults={
                "name": meta["comedian_name"],
                "comedian_type": meta["comedian_type"],
            },
        )

        # get_or_create Set
        set_obj, _ = Set.objects.get_or_create(
            episode=episode,
            set_number=set_number,
            defaults={
                "comedian": comedian,
                "start_seconds": meta["start_seconds"],
            },
        )

        # Wire up guests from the episode title
        for guest_name in meta.get("guests", []):
            guest_slug = re.sub(r"[^a-z0-9]+", "-", guest_name.lower()).strip("-")
            guest, _ = Comedian.objects.get_or_create(
                slug=guest_slug,
                defaults={"name": guest_name},
            )
            episode.guests.add(guest)

        # Idempotent: wipe existing beats for this set before reimporting
        deleted, _ = set_obj.beats.all().delete()
        if deleted:
            self.stdout.write(f"  Replaced {deleted} existing beats for set {set_number}")

        # Parse and bulk-create beats
        beats = []
        for line in beat_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            beats.append(
                Beat(
                    set=set_obj,
                    beat_number=row["beat_number"],
                    beat_type=row["beat_type"],
                    text=row["text"],
                    start_seconds=row["start_seconds"],
                )
            )

        Beat.objects.bulk_create(beats)
        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_number:02d} {meta['comedian_name']}: {len(beats)} beats"
            )
        )

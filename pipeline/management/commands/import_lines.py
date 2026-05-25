import json
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Comedian, Episode, Line, Set


class Command(BaseCommand):
    help = "Import annotated set JSON files from data/annotated_set_inbox/ into the database"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        annotated_set_inbox = data_dir / "annotated_set_inbox"
        processed_lines = data_dir / "processed_lines"

        annotated_files = sorted(annotated_set_inbox.glob("*.json"))
        if not annotated_files:
            self.stdout.write("No annotated set files found in annotated_set_inbox.")
            return

        for path in annotated_files:
            try:
                self._import(path)
                shutil.move(str(path), processed_lines / path.name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Failed {path.name}: {e}"))

    def _import(self, path):
        # Filename: {video_id}_set{NN}_{slug}.json
        match = re.match(r"^(.+)_set(\d+)_(.+)$", path.stem)
        if not match:
            raise ValueError(f"Filename does not match expected pattern: {path.name}")

        video_id = match.group(1)
        set_number = int(match.group(2))
        slug = match.group(3)

        meta = json.loads(path.read_text(encoding="utf-8"))

        episode, _ = Episode.objects.get_or_create(
            video_id=video_id,
            defaults={
                "episode_title": meta["episode_title"],
                "episode_url": meta["episode_url"],
                "published_at": meta.get("publish_date"),
            },
        )

        comedian, _ = Comedian.objects.get_or_create(
            slug=slug,
            defaults={
                "name": meta["comedian_name"],
                "comedian_type": meta["comedian_type"],
            },
        )

        set_obj, _ = Set.objects.get_or_create(
            episode=episode,
            set_number=set_number,
            defaults={
                "comedian": comedian,
                "start_seconds": meta["start_seconds"],
            },
        )

        for guest_name in meta.get("guests", []):
            guest_slug = re.sub(r"[^a-z0-9]+", "-", guest_name.lower()).strip("-")
            guest, _ = Comedian.objects.get_or_create(
                slug=guest_slug,
                defaults={"name": guest_name},
            )
            episode.guests.add(guest)

        # Idempotent: wipe existing lines for this set before reimporting
        deleted, _ = set_obj.lines.all().delete()
        if deleted:
            self.stdout.write(f"  Replaced {deleted} existing lines for set {set_number}")

        lines = []
        for i, line in enumerate(meta["lines"], start=1):
            lines.append(
                Line(
                    set=set_obj,
                    line_number=i,
                    label=line["label"],
                    text=line["text"],
                    start_seconds=line["start"],
                )
            )

        Line.objects.bulk_create(lines)
        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_number:02d} {meta['comedian_name']}: {len(lines)} lines"
            )
        )

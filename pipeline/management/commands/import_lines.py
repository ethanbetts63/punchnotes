import json
import re
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


class Command(BaseCommand):
    help = "Import bit-annotated set JSON files from data/4_bit_annotated_set_inbox/ into the database"

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

        # Lines — idempotent wipe before reimport
        deleted, _ = set_obj.lines.all().delete()
        if deleted:
            self.stdout.write(f"  Replaced {deleted} existing lines for set {set_number}")

        lines = []
        for line in meta["lines"]:
            lines.append(
                Line(
                    set=set_obj,
                    line_number=line["line_number"],
                    label=line["label"],
                    text=line["text"],
                    start_seconds=line["start"],
                )
            )
        Line.objects.bulk_create(lines)

        # Bits and beats — idempotent wipe before reimport
        set_obj.bits.all().delete()

        for bit_data in meta.get("bits", []):
            bit = Bit.objects.create(
                set=set_obj,
                bit_id=bit_data["bit_id"],
                premise=bit_data["premise"],
                line_start=bit_data["line_range"][0],
                line_end=bit_data["line_range"][1],
            )
            for beat_data in bit_data.get("beats", []):
                Beat.objects.create(
                    bit=bit,
                    beat_id=beat_data["beat_id"],
                    line_start=beat_data["line_range"][0],
                    line_end=beat_data["line_range"][1],
                    topics=beat_data.get("topics", []),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_number:02d} {meta['comedian_name']}: "
                f"{len(lines)} lines, {len(meta.get('bits', []))} bits"
            )
        )

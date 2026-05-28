import json
import re
import shutil
from collections import defaultdict


def _parse_episode_number(title: str) -> int | None:
    m = re.search(r"#(\d+)", title)
    return int(m.group(1)) if m else None

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


PREMISE_STRUCTURE_RULES = {
    "misdirect": ("implies", "but"),
    "reframe": ("could be",),
    "phonetic-match": ("sounds like", "and"),
    "double-meaning": ("can mean", "or"),
    "analogy": ("is like", "because both"),
    "hyperbole": ("so", "that"),
    "elephant-in-the-room": ("widely understood", "but rarely"),
}


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
        self._validate_bit_meta(meta)

        episode, _ = Episode.objects.get_or_create(
            video_id=video_id,
            defaults={
                "episode_number": _parse_episode_number(meta["episode_title"]),
                "episode_title": meta["episode_title"],
                "episode_url": meta["episode_url"],
                "published_at": meta.get("publish_date"),
            },
        )
        if episode.episode_number is None:
            episode.episode_number = _parse_episode_number(episode.episode_title)
            episode.save(update_fields=["episode_number"])

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
                "interview_end_line": meta.get("interview_end_line"),
                "interview_end_seconds": meta.get("interview_end_seconds"),
                "joke_book": meta.get("joke_book"),
            },
        )
        set_obj.comedian = comedian
        set_obj.start_seconds = meta["start_seconds"]
        set_obj.interview_end_line = meta.get("interview_end_line")
        set_obj.interview_end_seconds = meta.get("interview_end_seconds")
        set_obj.joke_book = meta.get("joke_book")
        set_obj.save(
            update_fields=[
                "comedian",
                "start_seconds",
                "interview_end_line",
                "interview_end_seconds",
                "joke_book",
            ]
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

        # Derive line ranges for each bit/beat from the flat lines array
        bit_lines = defaultdict(list)
        beat_lines = defaultdict(lambda: defaultdict(list))
        for line in meta["lines"]:
            b = line.get("bit")
            bt = line.get("beat")
            if b is not None:
                bit_lines[b].append(line["line_number"])
                if bt is not None:
                    beat_lines[b][bt].append(line["line_number"])

        for bit_num_str, bit_data in meta.get("bit_meta", {}).items():
            bit_num = int(bit_num_str)
            lns = bit_lines.get(bit_num, [])
            if not lns:
                continue
            bit = Bit.objects.create(
                set=set_obj,
                bit_id=f"bit_{bit_num:03d}",
                premise=bit_data.get("premise"),
                line_start=min(lns),
                line_end=max(lns),
            )
            for beat_num_str, beat_data in bit_data.get("beats", {}).items():
                beat_num = int(beat_num_str)
                blns = beat_lines[bit_num].get(beat_num, [])
                if not blns:
                    continue
                Beat.objects.create(
                    bit=bit,
                    beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
                    line_start=min(blns),
                    line_end=max(blns),
                    premise=beat_data.get("premise"),
                    joke_type=beat_data.get("joke_type") or None,
                    topics=beat_data.get("topics", []),
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"  {video_id} set{set_number:02d} {meta['comedian_name']}: "
                f"{len(lines)} lines, {len(meta.get('bit_meta', {}))} bits"
            )
        )

    def _validate_bit_meta(self, meta):
        errors = []
        for bit_num, bit_data in meta.get("bit_meta", {}).items():
            for beat_num, beat_data in bit_data.get("beats", {}).items():
                location = f"bit {bit_num} beat {beat_num}"
                joke_type = beat_data.get("joke_type")
                premise = beat_data.get("premise")

                if joke_type not in PREMISE_STRUCTURE_RULES:
                    accepted = ", ".join(sorted(PREMISE_STRUCTURE_RULES))
                    errors.append(
                        f"{location}: joke_type must be one of [{accepted}], got {joke_type!r}"
                    )
                    continue

                if not isinstance(premise, str) or not premise.strip():
                    errors.append(f"{location}: premise is required for joke_type {joke_type!r}")
                    continue

                premise_lower = premise.lower()
                missing = [
                    required
                    for required in PREMISE_STRUCTURE_RULES[joke_type]
                    if required not in premise_lower
                ]
                if missing:
                    required = ", ".join(
                        f'"{phrase}"' for phrase in PREMISE_STRUCTURE_RULES[joke_type]
                    )
                    errors.append(
                        f"{location}: {joke_type} premise must contain {required}; "
                        f"missing {', '.join(f'{phrase!r}' for phrase in missing)}"
                    )

        if errors:
            raise ValueError("Invalid bit_meta:\n  " + "\n  ".join(errors))

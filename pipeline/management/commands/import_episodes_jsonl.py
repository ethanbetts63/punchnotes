import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pipeline.models import Episode


DEFAULT_JSONL_NAME = "full_kt_episodes.jsonl"
EPISODE_NUMBER_PATTERN = re.compile(r"#\s*(\d+)")

FIELD_MAP = {
    "episode_number": "episode_number",
    "episode_title": "episode_title",
    "episode_url": "episode_url",
    "duration_seconds": "duration_seconds",
    "published_at": "published_at",
    "view_count": "view_count",
    "like_count": "like_count",
    "comment_count": "comment_count",
}


def _episode_number(title: str | None) -> int | None:
    if not title:
        return None
    match = EPISODE_NUMBER_PATTERN.search(title)
    return int(match.group(1)) if match else None


class Command(BaseCommand):
    help = "Import episode metadata from a JSONL file produced by fetch_episodes"

    def add_arguments(self, parser):
        parser.add_argument(
            "jsonl_path",
            nargs="?",
            help=f"Path to a fetch_episodes JSONL output file. Defaults to pipeline/data/{DEFAULT_JSONL_NAME}.",
        )

    def handle(self, *args, **options):
        jsonl_path = (
            Path(options["jsonl_path"])
            if options["jsonl_path"]
            else settings.PIPELINE_DATA_DIR / DEFAULT_JSONL_NAME
        )
        if not jsonl_path.exists():
            raise CommandError(f"File not found: {jsonl_path}")

        created = updated = skipped = failed = 0
        self.stdout.write(f"Importing {jsonl_path}...")

        with jsonl_path.open("r", encoding="utf-8") as input_file:
            for line_number, line in enumerate(input_file, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    video_id = data["video_id"]
                    defaults = {
                        model_field: data[source_field]
                        for source_field, model_field in FIELD_MAP.items()
                        if source_field in data and data[source_field] is not None
                    }
                    if "episode_url" not in defaults:
                        defaults["episode_url"] = f"https://www.youtube.com/watch?v={video_id}"
                    if "episode_title" not in defaults:
                        defaults["episode_title"] = data.get("title") or video_id
                    if "episode_number" not in defaults:
                        parsed_number = _episode_number(defaults.get("episode_title"))
                        if parsed_number is not None:
                            defaults["episode_number"] = parsed_number

                    _, was_created = Episode.objects.update_or_create(
                        video_id=video_id,
                        defaults=defaults,
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    failed += 1
                    skipped += 1
                    self.stdout.write(self.style.ERROR(f"  line {line_number}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created} created, {updated} updated, {skipped} skipped, {failed} failed."
            )
        )

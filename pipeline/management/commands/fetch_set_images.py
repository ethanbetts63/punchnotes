import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from pipeline.models import Set
from pipeline.scripts.grab_set_image import (
    DEFAULT_OUTPUT_DIR,
    default_output_path,
    download_clip,
    grab_frame,
    youtube_url,
)


HISTORY_NAME = "set_image_fetch_history.jsonl"


def append_history(history_path, record):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with history_path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_history(history_path):
    latest = {}
    if not history_path.exists():
        return latest

    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        set_id = record.get("set_id")
        if set_id is None:
            continue
        latest[int(set_id)] = record

    return latest


def file_exists(filename, *dirs):
    for directory in dirs:
        if (directory / filename).exists():
            return True
    return False


def set_record(set_obj, status, **extra):
    return {
        "set_id": set_obj.id,
        "video_id": set_obj.episode.video_id,
        "episode_number": set_obj.episode.episode_number,
        "set_number": set_obj.set_number,
        "comedian_slug": set_obj.comedian.slug,
        "comedian_name": set_obj.comedian.name,
        "status": status,
        **extra,
    }


class Command(BaseCommand):
    help = "Fetch missing Set images from YouTube into pipeline/data/4_set_images_inbox."

    def add_arguments(self, parser):
        parser.add_argument("--set-id", action="append", type=int, help="Fetch one Set id. Can be repeated.")
        parser.add_argument("--limit", type=int, help="Maximum number of fetch attempts.")
        parser.add_argument("--offset", type=float, default=30, help="Seconds after set.start_seconds to capture.")
        parser.add_argument("--clip-duration", type=float, default=0.05, help="Temporary clip duration in seconds.")
        parser.add_argument("--width", type=int, default=480, help="Output image width in pixels.")
        parser.add_argument(
            "--quality",
            type=int,
            default=4,
            help="ffmpeg JPEG quality. Lower is higher quality; 2-5 is a useful range.",
        )
        parser.add_argument(
            "--cookies-from-browser",
            choices=["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"],
            help="Pass browser cookies to yt-dlp for age-gated videos.",
        )
        parser.add_argument("--cookies", help="Path to a Netscape cookies.txt file for yt-dlp.")
        parser.add_argument("--retry-failures", action="store_true", help="Retry sets marked failed in history.")
        parser.add_argument("--replace", action="store_true", help="Fetch even when a DB image or image file exists.")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched without hitting YouTube.")

    def handle(self, *args, **options):
        if options["clip_duration"] <= 0:
            self.stderr.write(self.style.ERROR("--clip-duration must be positive"))
            return
        if options["width"] < 1:
            self.stderr.write(self.style.ERROR("--width must be positive"))
            return
        if options["quality"] < 1:
            self.stderr.write(self.style.ERROR("--quality must be positive"))
            return

        data_dir = settings.PIPELINE_DATA_DIR
        inbox_dir = DEFAULT_OUTPUT_DIR
        archive_dir = data_dir / "set_images_archive"
        public_dir = settings.BASE_DIR / "frontend" / "public" / "set-images"
        history_path = data_dir / HISTORY_NAME

        if not options["dry_run"]:
            inbox_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.mkdir(parents=True, exist_ok=True)
            public_dir.mkdir(parents=True, exist_ok=True)

        history = load_history(history_path)
        sets = self.get_sets(options)
        if not sets:
            self.stdout.write("No sets need images.")
            return

        fetched = skipped = failed = attempted = 0
        self.stdout.write(f"Checking {len(sets)} set(s) for missing images...")

        for set_obj in sets:
            if options["limit"] is not None and attempted >= options["limit"]:
                break

            capture_seconds = set_obj.start_seconds + options["offset"]
            output_path = default_output_path(
                set_obj.episode.video_id,
                capture_seconds,
                set_obj.episode.episode_number,
                set_obj.set_number,
                set_obj.comedian.name,
                set_obj.id,
            )
            filename = output_path.name
            latest = history.get(set_obj.id)

            if not options["replace"]:
                if set_obj.image_url:
                    skipped += 1
                    continue

                if latest and latest.get("status") == "failed" and not options["retry_failures"]:
                    skipped += 1
                    continue

                if latest and latest.get("status") == "captured" and file_exists(
                    filename, inbox_dir, archive_dir, public_dir
                ):
                    skipped += 1
                    continue

                if file_exists(filename, inbox_dir, public_dir):
                    skipped += 1
                    continue

            attempted += 1
            args = SimpleNamespace(
                video_id=set_obj.episode.video_id,
                url=None,
                episode_number=set_obj.episode.episode_number,
                set_number=set_obj.set_number,
                comic_name=set_obj.comedian.name,
                timestamp=set_obj.start_seconds,
                offset=options["offset"],
                clip_duration=options["clip_duration"],
                width=options["width"],
                quality=options["quality"],
                cookies_from_browser=options["cookies_from_browser"],
                cookies=options["cookies"],
            )
            source_url = youtube_url(video_id=set_obj.episode.video_id)

            self.stdout.write(
                f"{'Would fetch' if options['dry_run'] else 'Fetching'} "
                f"KT{set_obj.episode.episode_number} set {set_obj.set_number} "
                f"({set_obj.comedian.name}) -> {filename}"
            )

            if options["dry_run"]:
                fetched += 1
                continue

            try:
                self.fetch_one(args, source_url, capture_seconds, output_path)
            except Exception as exc:
                failed += 1
                append_history(
                    history_path,
                    set_record(
                        set_obj,
                        "failed",
                        capture_seconds=capture_seconds,
                        output=filename,
                        error=str(exc),
                    ),
                )
                self.stdout.write(self.style.WARNING(f"  failed: {exc}"))
                continue

            fetched += 1
            append_history(
                history_path,
                set_record(
                    set_obj,
                    "captured",
                    capture_seconds=capture_seconds,
                    output=filename,
                ),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {fetched} fetched, {skipped} skipped, {failed} failed."
            )
        )

    def get_sets(self, options):
        queryset = (
            Set.objects
            .select_related("episode", "comedian")
            .exclude(episode__video_id__isnull=True)
            .exclude(episode__video_id="")
            .exclude(episode__episode_number__isnull=True)
            .order_by("-episode__episode_number", "set_number", "id")
        )

        if options["set_id"]:
            queryset = queryset.filter(id__in=options["set_id"])
        elif not options["replace"]:
            queryset = queryset.filter(Q(image_url__isnull=True) | Q(image_url=""))

        return list(queryset)

    def fetch_one(self, args, source_url, capture_seconds, output_path):
        half_clip = args.clip_duration / 2
        clip_start = max(capture_seconds - half_clip, 0)
        clip_end = capture_seconds + half_clip
        relative_seconds = capture_seconds - clip_start

        with tempfile.TemporaryDirectory(prefix="punchpedia_frame_") as tmp:
            clip_path = download_clip(source_url, args, clip_start, clip_end, Path(tmp))
            grab_frame(clip_path, relative_seconds, output_path, args.width, args.quality)

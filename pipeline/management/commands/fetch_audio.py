import json
import re
from datetime import datetime, timezone

import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Episode


INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
HISTORY_NAME = "audio_fetch_history.jsonl"


def safe_filename_part(value):
    value = INVALID_FILENAME_CHARS.sub("-", str(value))
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip(". ") or "unknown"


def find_audio(video_id, *audio_dirs):
    """Return an existing audio Path for a video_id, or None."""
    for audio_dir in audio_dirs:
        matches = list(audio_dir.glob(f"{video_id} - *.*"))
        if matches:
            return matches[0]
    return None


def load_failed_video_ids(history_path):
    failed = set()
    if not history_path.exists():
        return failed

    for line in history_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        video_id = record.get("video_id")
        status = record.get("status")
        if not video_id:
            continue
        if status == "failed":
            failed.add(video_id)
        elif status == "downloaded":
            failed.discard(video_id)
    return failed


def append_history(history_path, record):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with history_path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def ydl_options(options, extra=None):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }
    if options.get("cookies_from_browser"):
        ydl_opts["cookiesfrombrowser"] = (options["cookies_from_browser"],)
    if options.get("cookies"):
        ydl_opts["cookiefile"] = options["cookies"]
    if extra:
        ydl_opts.update(extra)
    return ydl_opts


def episode_filename(episode):
    publish_date = episode.published_at.isoformat() if episode.published_at else "unknown-date"
    title = safe_filename_part(episode.episode_title)
    return f"{episode.video_id} - {publish_date} - {title}.%(ext)s"


class Command(BaseCommand):
    help = "Download missing Episode audio into pipeline/data/0_audio_inbox"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cookies-from-browser",
            choices=["brave", "chrome", "chromium", "edge", "firefox", "opera", "safari", "vivaldi"],
            help="Pass browser cookies to yt-dlp for age-gated videos.",
        )
        parser.add_argument(
            "--cookies",
            help="Path to a Netscape cookies.txt file for yt-dlp.",
        )
        parser.add_argument(
            "--retry-failures",
            action="store_true",
            help=f"Retry videos marked failed in pipeline/data/{HISTORY_NAME}.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Maximum number of download attempts for this run.",
        )

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR
        inbox_dir = data_dir / "0_audio_inbox"
        archive_dir = data_dir / "audio_archive"
        history_path = data_dir / HISTORY_NAME
        inbox_dir.mkdir(parents=True, exist_ok=True)
        archive_dir.mkdir(parents=True, exist_ok=True)

        failed_video_ids = load_failed_video_ids(history_path)
        retry_failures = options["retry_failures"]
        limit = options.get("limit")

        episodes = list(
            Episode.objects.exclude(video_id__isnull=True)
            .exclude(video_id="")
            .order_by("-episode_number", "video_id")
        )
        if not episodes:
            self.stdout.write("No Episode rows found. Import episode metadata first.")
            return

        self.stdout.write(f"Checking {len(episodes)} episode(s) for missing audio...")

        downloaded = already_present = skipped_failed = failed = attempted = 0
        for episode in episodes:
            video_id = episode.video_id
            existing_audio = find_audio(video_id, inbox_dir, archive_dir)
            if existing_audio:
                already_present += 1
                continue

            if video_id in failed_video_ids and not retry_failures:
                skipped_failed += 1
                continue

            if limit is not None and attempted >= limit:
                break

            attempted += 1
            episode_url = episode.episode_url or f"https://www.youtube.com/watch?v={video_id}"
            outtmpl = str(inbox_dir / episode_filename(episode))
            download_opts = ydl_options(
                options,
                {
                    "format": "bestaudio/best",
                    "outtmpl": outtmpl,
                },
            )

            self.stdout.write(f"  [{video_id}] downloading audio...")
            try:
                with yt_dlp.YoutubeDL(download_opts) as ydl:
                    ydl.download([episode_url])
            except yt_dlp.utils.DownloadError as e:
                failed += 1
                append_history(
                    history_path,
                    {
                        "video_id": video_id,
                        "episode_number": episode.episode_number,
                        "status": "failed",
                        "error": str(e),
                    },
                )
                self.stdout.write(self.style.WARNING(f"  [{video_id}] failed: {e}"))
                continue

            downloaded += 1
            append_history(
                history_path,
                {
                    "video_id": video_id,
                    "episode_number": episode.episode_number,
                    "status": "downloaded",
                },
            )
            self.stdout.write(f"  [{video_id}] done")

        self.stdout.write(
            self.style.SUCCESS(
                "Done. "
                f"{downloaded} downloaded, "
                f"{already_present} already present, "
                f"{skipped_failed} skipped previous failures, "
                f"{failed} failed."
            )
        )

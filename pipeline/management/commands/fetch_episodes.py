import json
import re
from datetime import datetime, timezone

import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


# This command is intentionally scrape-only: it does not write to the database.
# YouTube and yt-dlp calls are the fragile part of the episode metadata pipeline,
# so each episode is appended to a JSONL file immediately after it is scraped and
# the file is flushed before moving to the next entry. That means a network error,
# process interruption, or long full scrape still leaves durable partial output.
#
# There are two scrape modes:
#   --basic reads the playlist in flat mode. It is fast and captures stable
#   playlist-level metadata: video_id, episode number, title, URL, duration, and
#   publish date when available.
#   --full starts with the same playlist scan, then opens each individual video
#   page with yt-dlp. It is slower, but captures engagement fields needed by the
#   frontend sort controls: view_count, like_count, and comment_count.
#
# Runs are resumable per mode. If a matching JSONL file already exists, the
# command appends to the newest one and skips any video_id already present in
# that file. For example, interrupting `python manage.py fetch_episodes --full`
# and rerunning it will continue writing to the newest `full-*.jsonl` file
# instead of starting the scrape from episode 1 again.
#
# To load the saved records into the database, run import_episodes_jsonl against
# the emitted JSONL file. Keeping scrape and import separate makes the raw scrape
# auditable, repeatable, and safe to resume manually if YouTube blocks or fails
# partway through a run.

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLy4mvfOQOs8Aw527rECOiIwvqXn525c8s"
KT_PATTERN = re.compile(r"KT\s*#(\d+)", re.IGNORECASE)


def _parse_upload_date(raw: str | None) -> str | None:
    if raw and len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


def _episode_number(title: str) -> int | None:
    match = KT_PATTERN.search(title)
    return int(match.group(1)) if match else None


def _record_from_entry(entry: dict, mode: str) -> dict:
    video_id = entry["id"]
    title = entry.get("title", "")
    return {
        "type": "episode",
        "fetch_mode": mode,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "episode_number": _episode_number(title),
        "episode_title": title,
        "episode_url": f"https://www.youtube.com/watch?v={video_id}",
        "duration_seconds": entry.get("duration"),
        "published_at": _parse_upload_date(entry.get("upload_date")),
    }


def _latest_output_path(output_dir, mode: str):
    return max(output_dir.glob(f"{mode}-*.jsonl"), key=lambda p: p.stat().st_mtime, default=None)


def _seen_video_ids(path) -> set[str]:
    seen = set()
    if not path or not path.exists():
        return seen

    with path.open("r", encoding="utf-8") as input_file:
        for line in input_file:
            line = line.strip()
            if not line:
                continue
            try:
                video_id = json.loads(line).get("video_id")
            except json.JSONDecodeError:
                continue
            if video_id:
                seen.add(video_id)
    return seen


class Command(BaseCommand):
    help = "Fetch Kill Tony episode metadata to a JSONL file without writing to the database"

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--basic",
            action="store_true",
            help="Fast playlist-only scrape.",
        )
        mode.add_argument(
            "--full",
            action="store_true",
            help="Playlist scrape plus per-video engagement stats.",
        )

    def handle(self, *args, **options):
        mode = "full" if options["full"] else "basic"
        output_dir = settings.PIPELINE_DATA_DIR / "episode_fetches"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = _latest_output_path(output_dir, mode)
        if output_path is None:
            output_path = output_dir / f"{mode}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.jsonl"
        seen_video_ids = _seen_video_ids(output_path)

        self.stdout.write(f"Scanning playlist ({mode})...")
        flat_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            info = ydl.extract_info(PLAYLIST_URL, download=False)

        entries = [entry for entry in info.get("entries", []) if entry.get("id")]
        if not entries:
            raise CommandError("No playlist entries found.")

        self.stdout.write(f"  {len(entries)} entries found")
        self.stdout.write(f"  resuming {output_path}")
        self.stdout.write(f"  {len(seen_video_ids)} existing record(s) will be skipped")

        written = skipped = full_failed = 0
        video_opts = {"quiet": True, "no_warnings": True}
        with output_path.open("a", encoding="utf-8") as output:
            for i, entry in enumerate(entries, 1):
                record = _record_from_entry(entry, mode)
                video_id = record["video_id"]

                if video_id in seen_video_ids:
                    skipped += 1
                    continue

                if mode == "full":
                    self.stdout.write(f"  [{i}/{len(entries)}] {video_id} - fetching video details")
                    try:
                        with yt_dlp.YoutubeDL(video_opts) as ydl:
                            video_info = ydl.extract_info(record["episode_url"], download=False)

                        detailed_title = video_info.get("title") or record["episode_title"]
                        record.update(
                            {
                                "episode_number": _episode_number(detailed_title),
                                "episode_title": detailed_title,
                                "duration_seconds": video_info.get("duration") or record["duration_seconds"],
                                "published_at": _parse_upload_date(video_info.get("upload_date")) or record["published_at"],
                                "view_count": video_info.get("view_count"),
                                "like_count": video_info.get("like_count"),
                                "comment_count": video_info.get("comment_count"),
                            }
                        )
                    except Exception as e:
                        full_failed += 1
                        record["detail_error"] = str(e)
                        self.stdout.write(self.style.ERROR(f"    failed: {e}"))
                else:
                    self.stdout.write(f"  [{i}/{len(entries)}] {video_id}")

                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
                written += 1
                seen_video_ids.add(video_id)

        self.stdout.write(f"  {written} record(s) written")
        self.stdout.write(f"  {skipped} existing record(s) skipped")
        if mode == "full":
            self.stdout.write(f"  {full_failed} detail fetch(es) failed")
        self.stdout.write(self.style.SUCCESS(f"Done: {output_path}"))

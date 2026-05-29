import json
import time

import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Episode

SLEEP_BETWEEN = 2  # seconds between requests


class Command(BaseCommand):
    help = "Fetch per-video engagement stats (views, likes, comments) and write to inbox"

    def handle(self, *args, **options):
        inbox = settings.PIPELINE_DATA_DIR / "episode_details_inbox"
        inbox.mkdir(parents=True, exist_ok=True)

        episodes = list(
            Episode.objects.filter(view_count__isnull=True)
            .exclude(video_id__isnull=True)
            .order_by("episode_number")
        )

        if not episodes:
            self.stdout.write("All episodes already have engagement data.")
            return

        self.stdout.write(f"{len(episodes)} episode(s) to scrape...")

        ydl_opts = {"quiet": True, "no_warnings": True}

        for i, ep in enumerate(episodes, 1):
            out_file = inbox / f"{ep.video_id}.json"
            if out_file.exists():
                self.stdout.write(f"  [{i}/{len(episodes)}] {ep.video_id} — already in inbox, skipping")
                continue

            self.stdout.write(f"  [{i}/{len(episodes)}] {ep.video_id} — fetching...")
            try:
                url = f"https://www.youtube.com/watch?v={ep.video_id}"
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                payload = {
                    "video_id": ep.video_id,
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "comment_count": info.get("comment_count"),
                }
                out_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    views={payload['view_count']}  likes={payload['like_count']}  "
                        f"comments={payload['comment_count']}"
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    failed: {e}"))

            if i < len(episodes):
                time.sleep(SLEEP_BETWEEN)

        self.stdout.write(self.style.SUCCESS("Done."))

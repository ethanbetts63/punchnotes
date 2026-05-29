import re
from datetime import date

import yt_dlp
from django.core.management.base import BaseCommand

from pipeline.models import Episode

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLy4mvfOQOs8Aw527rECOiIwvqXn525c8s"
KT_PATTERN = re.compile(r"KT\s*#(\d+)", re.IGNORECASE)


def _parse_upload_date(raw: str | None) -> date | None:
    if raw and len(raw) == 8:
        try:
            return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
        except ValueError:
            pass
    return None


class Command(BaseCommand):
    help = "Fetch Kill Tony episode metadata from the full playlist and upsert into Episode table"

    def handle(self, *args, **options):
        self.stdout.write("Scanning playlist...")
        flat_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
        with yt_dlp.YoutubeDL(flat_opts) as ydl:
            info = ydl.extract_info(PLAYLIST_URL, download=False)

        entries = info.get("entries", [])
        self.stdout.write(f"  {len(entries)} entries in playlist")

        created = updated = 0
        for entry in entries:
            video_id = entry.get("id")
            if not video_id:
                continue
            title = entry.get("title", "")
            m = KT_PATTERN.search(title)
            _, was_created = Episode.objects.update_or_create(
                video_id=video_id,
                defaults={
                    "episode_number": int(m.group(1)) if m else None,
                    "episode_title": title,
                    "episode_url": f"https://www.youtube.com/watch?v={video_id}",
                    "duration_seconds": entry.get("duration"),
                    "published_at": _parse_upload_date(entry.get("upload_date")),
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(f"  {created} created, {updated} updated")
        self.stdout.write(self.style.SUCCESS("Done"))

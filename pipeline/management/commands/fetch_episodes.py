import re

import yt_dlp
from django.core.management.base import BaseCommand

from pipeline.models import Episode

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLckDfvgNRRkhpzJ0bJW2NrPvFXMRbgn5N"
KT_PATTERN = re.compile(r"KT\s*#(\d+)", re.IGNORECASE)



class Command(BaseCommand):
    help = "Fetch Kill Tony episode metadata from the full playlist and upsert into Episode table"

    def handle(self, *args, **options):
        # --- Phase 1: flat playlist scan ---
        self.stdout.write("Phase 1: scanning playlist...")
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
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(f"  {created} created, {updated} updated")

        self.stdout.write(self.style.SUCCESS("Done"))

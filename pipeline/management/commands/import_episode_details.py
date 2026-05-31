import json
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Episode


class Command(BaseCommand):
    help = "Import scraped episode engagement stats from inbox into the database"

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR
        inbox = data_dir / "episode_details_inbox"
        archive = data_dir / "episode_details_archive"
        archive.mkdir(parents=True, exist_ok=True)

        files = sorted(inbox.glob("*.json"))
        if not files:
            self.stdout.write(f"No files in {inbox}")
            return

        self.stdout.write(f"Importing {len(files)} file(s)...")

        updated = skipped = 0
        for path in files:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                video_id = data["video_id"]

                episode = Episode.objects.filter(video_id=video_id).first()
                if episode:
                    view_count = data.get("view_count")
                    like_count = data.get("like_count")
                    episode.view_count = view_count
                    episode.like_count = like_count
                    episode.comment_count = data.get("comment_count")
                    episode.view_like_ratio = (
                        like_count / view_count
                        if view_count and like_count
                        else None
                    )
                    episode.save(update_fields=["view_count", "like_count", "comment_count", "view_like_ratio"])
                    self.stdout.write(self.style.SUCCESS(f"  {video_id} — updated"))
                    updated += 1
                else:
                    self.stdout.write(self.style.WARNING(f"  {video_id} — no matching episode, skipping"))
                    skipped += 1

                shutil.move(str(path), archive / path.name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  {path.name} — failed: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Done. {updated} updated, {skipped} skipped."))

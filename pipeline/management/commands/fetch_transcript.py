import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from youtube_transcript_api import YouTubeTranscriptApi


class Command(BaseCommand):
    help = "Fetch transcript for the first entry in data/transcript_todos.jsonl"

    def handle(self, *args, **options):
        todo_path = settings.BASE_DIR / "data" / "transcript_todos.jsonl"
        inbox_path = settings.BASE_DIR / "data" / "inbox"

        lines = [l.strip() for l in todo_path.read_text().splitlines() if l.strip()]
        if not lines:
            self.stdout.write("No entries in todo file.")
            return

        entry = json.loads(lines[0])
        video_id = entry["video_id"]

        self.stdout.write(f"Fetching transcript for {video_id}...")

        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        out_path = inbox_path / f"{video_id}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for segment in transcript:
                f.write(json.dumps({"video_id": video_id, **segment}) + "\n")

        self.stdout.write(self.style.SUCCESS(f"Saved {len(transcript)} segments to {out_path}"))

import json
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from youtube_transcript_api import YouTubeTranscriptApi


def fetch_episode_title(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["title"]


class Command(BaseCommand):
    help = "Fetch transcript for the first entry in data/transcript_todos.jsonl"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        todo_path = data_dir / "transcript_todos.jsonl"
        history_path = data_dir / "scrape_history.jsonl"
        inbox_path = data_dir / "transcript_inbox"

        lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
        if not lines:
            self.stdout.write("No entries in todo file.")
            return

        first_line = lines[0]
        entry = json.loads(first_line)
        video_id = entry["video_id"]

        self.stdout.write(f"Fetching transcript for {video_id}...")

        episode_title = fetch_episode_title(video_id)
        episode_url = f"https://www.youtube.com/watch?v={video_id}"
        self.stdout.write(f"Title: {episode_title}")

        transcript = YouTubeTranscriptApi().fetch(video_id)

        out_path = inbox_path / f"{video_id}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            episode_meta = {"type": "episode_meta", "video_id": video_id, "episode_title": episode_title, "episode_url": episode_url}
            f.write(json.dumps(episode_meta) + "\n")
            for segment in transcript:
                f.write(json.dumps({"video_id": video_id, "text": segment.text, "start": segment.start, "duration": segment.duration}) + "\n")

        self.stdout.write(self.style.SUCCESS(f"Saved {len(transcript)} segments to {out_path}"))

        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({**entry, "episode_title": episode_title}) + "\n")

        remaining = lines[1:]
        todo_path.write_text(("\n".join(remaining) + "\n") if remaining else "")

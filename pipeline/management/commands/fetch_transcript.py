import json
import urllib.request
from pathlib import Path

import whisper
import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand


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
        archive_path = data_dir / "transcript_archive"
        audio_dir = data_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        archive_path.mkdir(exist_ok=True)

        lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
        if not lines:
            self.stdout.write("No entries in todo file.")
            return

        entry = json.loads(lines[0])
        video_id = entry["video_id"]

        self.stdout.write(f"Fetching transcript for {video_id}...")

        episode_title = fetch_episode_title(video_id)
        episode_url = f"https://www.youtube.com/watch?v={video_id}"
        self.stdout.write(f"Title: {episode_title}")

        existing = list(audio_dir.glob(f"{video_id}.*"))
        if existing:
            audio_path = existing[0]
            self.stdout.write(f"Using cached audio: {audio_path.name}")
        else:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(audio_dir / f"{video_id}.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            self.stdout.write("Downloading audio...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([episode_url])
            audio_path = next(audio_dir.glob(f"{video_id}.*"))

        self.stdout.write("Transcribing with Whisper small.en (this may take a while)...")
        model = whisper.load_model("small.en")
        result = model.transcribe(
            str(audio_path),
            language="en",
            fp16=False,
            verbose=True,
            condition_on_previous_text=False,
            suppress_tokens=[],
            beam_size=1,
        )

        segments = result["segments"]
        meta = {
            "type": "episode_meta",
            "video_id": video_id,
            "episode_title": episode_title,
            "episode_url": episode_url,
        }

        # Full copy → archive (keeps duration and full-precision start)
        archive_doc = {
            **meta,
            "segments": [
                {
                    "text": seg["text"].strip(),
                    "start": seg["start"],
                    "duration": seg["end"] - seg["start"],
                }
                for seg in segments
            ],
        }
        archive_file = archive_path / f"{video_id}.json"
        archive_file.write_text(json.dumps(archive_doc, indent=2), encoding="utf-8")
        self.stdout.write(f"Archived to {archive_file}")

        # Simplified copy → inbox (no duration, start floored to whole second)
        inbox_doc = {
            **meta,
            "segments": [
                {
                    "text": seg["text"].strip(),
                    "start": int(seg["start"]),
                }
                for seg in segments
            ],
        }
        inbox_file = inbox_path / f"{video_id}.json"
        inbox_file.write_text(json.dumps(inbox_doc, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Saved {len(segments)} segments to {inbox_file}"))

        with open(history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({**entry, "episode_title": episode_title}) + "\n")

        remaining = lines[1:]
        todo_path.write_text(("\n".join(remaining) + "\n") if remaining else "")

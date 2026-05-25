import json
import urllib.request
from pathlib import Path

import whisper
import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand


def dump_episode(doc):
    """Pretty-print top-level fields, one compact line per segment."""
    non_seg = [(k, v) for k, v in doc.items() if k != "segments"]
    has_segs = "segments" in doc
    parts = ["{"]
    for i, (k, v) in enumerate(non_seg):
        comma = "," if i < len(non_seg) - 1 or has_segs else ""
        parts.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    if has_segs:
        parts.append('  "segments": [')
        segs = doc["segments"]
        for i, s in enumerate(segs):
            comma = "," if i < len(segs) - 1 else ""
            parts.append(f"    {json.dumps(s, ensure_ascii=False)}{comma}")
        parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


def fetch_episode_title(video_id):
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["title"]


class Command(BaseCommand):
    help = "Download all audio in transcript_todos.jsonl, then transcribe each one"

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

        entries = [json.loads(l) for l in lines]

        # --- Phase 1: download all audio files that aren't cached yet ---
        self.stdout.write(f"Phase 1: downloading audio for {len(entries)} entries...")
        for entry in entries:
            video_id = entry["video_id"]
            existing = list(audio_dir.glob(f"{video_id}.*"))
            if existing:
                self.stdout.write(f"  [{video_id}] already cached, skipping download")
                continue
            episode_url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(audio_dir / f"{video_id}.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
            }
            self.stdout.write(f"  [{video_id}] downloading...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([episode_url])
            self.stdout.write(f"  [{video_id}] done")

        self.stdout.write("Phase 1 complete.\n")

        # --- Phase 2: transcribe one by one ---
        self.stdout.write(f"Phase 2: transcribing {len(entries)} entries...")
        model = whisper.load_model("small.en")

        for entry in entries:
            video_id = entry["video_id"]
            episode_url = f"https://www.youtube.com/watch?v={video_id}"

            self.stdout.write(f"\n[{video_id}] Fetching title...")
            episode_title = fetch_episode_title(video_id)
            self.stdout.write(f"[{video_id}] Title: {episode_title}")

            audio_path = next(audio_dir.glob(f"{video_id}.*"))

            self.stdout.write(f"[{video_id}] Transcribing with Whisper small.en...")
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
            archive_file.write_text(dump_episode(archive_doc), encoding="utf-8")
            self.stdout.write(f"[{video_id}] Archived to {archive_file}")

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
            inbox_file.write_text(dump_episode(inbox_doc), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[{video_id}] Saved {len(segments)} segments to {inbox_file}"))

            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({**entry, "episode_title": episode_title}) + "\n")

            # Remove this entry from the todo file immediately after processing
            remaining_lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
            remaining_lines = [l for l in remaining_lines if json.loads(l)["video_id"] != video_id]
            todo_path.write_text(("\n".join(remaining_lines) + "\n") if remaining_lines else "")

        self.stdout.write(self.style.SUCCESS("\nAll done."))

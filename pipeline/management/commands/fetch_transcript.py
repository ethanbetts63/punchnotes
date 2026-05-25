import json
from pathlib import Path

import whisper
import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand

# YouTube video IDs are always 11 characters.
# Audio files are named "{video_id} - {title}.{ext}" so the title can be
# recovered offline without a network call.
VIDEO_ID_LEN = 11


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


def fetch_episode_meta(video_id):
    """Return (title, publish_date) for a YouTube video using yt_dlp (no download)."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    raw = info.get("upload_date", "")  # YYYYMMDD or empty
    publish_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:]}" if len(raw) == 8 else None
    return info["title"], publish_date


def find_audio(audio_dir, video_id):
    """Return the audio Path for a video_id, or None if not cached."""
    matches = list(audio_dir.glob(f"{video_id} - *.*"))
    return matches[0] if matches else None


def title_from_audio(audio_path):
    """Parse the episode title from a '{video_id} - {title}.ext' filename."""
    return audio_path.stem[VIDEO_ID_LEN + 3:]  # skip "{id} - "


class Command(BaseCommand):
    help = "Download all audio in transcript_todos.jsonl, then transcribe each one"

    def add_arguments(self, parser):
        parser.add_argument(
            "--local-only",
            action="store_true",
            help="Skip downloads; only transcribe entries whose audio is already cached",
        )

    def handle(self, *args, **options):
        local_only = options["local_only"]
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
        publish_dates = {}  # video_id -> "YYYY-MM-DD" or None; populated in Phase 1

        # --- Phase 1: download all audio files that aren't cached yet ---
        if local_only:
            self.stdout.write("--local-only: skipping downloads.")
        else:
            self.stdout.write(f"Phase 1: downloading audio for {len(entries)} entries...")
            for entry in entries:
                video_id = entry["video_id"]
                if find_audio(audio_dir, video_id):
                    self.stdout.write(f"  [{video_id}] already cached, skipping download")
                    continue
                self.stdout.write(f"  [{video_id}] fetching metadata...")
                title, publish_date = fetch_episode_meta(video_id)
                publish_dates[video_id] = publish_date
                episode_url = f"https://www.youtube.com/watch?v={video_id}"
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": str(audio_dir / f"{video_id} - {title}.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                }
                self.stdout.write(f"  [{video_id}] downloading \"{title}\" ({publish_date})...")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([episode_url])
                self.stdout.write(f"  [{video_id}] done")
            self.stdout.write("Phase 1 complete.\n")

        # --- Phase 2: transcribe one by one ---
        to_process = [(e, find_audio(audio_dir, e["video_id"])) for e in entries]
        to_process = [(e, p) for e, p in to_process if p is not None]
        skipped = len(entries) - len(to_process)
        if skipped:
            self.stdout.write(f"Skipping {skipped} entries with no cached audio.")
        self.stdout.write(f"Phase 2: transcribing {len(to_process)} entries...")
        model = whisper.load_model("small.en")

        for entry, audio_path in to_process:
            video_id = entry["video_id"]
            episode_title = title_from_audio(audio_path)
            episode_url = f"https://www.youtube.com/watch?v={video_id}"

            if video_id not in publish_dates:
                # Audio was already cached in Phase 1 (or --local-only); fetch metadata now.
                self.stdout.write(f"  [{video_id}] fetching metadata for publish date...")
                _, publish_dates[video_id] = fetch_episode_meta(video_id)
            publish_date = publish_dates[video_id]

            self.stdout.write(f"\n[{video_id}] Title: {episode_title}")
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
                "publish_date": publish_date,
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

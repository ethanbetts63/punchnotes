import json
from pathlib import Path

import whisper
import yt_dlp
from django.conf import settings
from django.core.management.base import BaseCommand

# YouTube video IDs are always 11 characters.
# Audio files are named "{video_id} - {YYYY-MM-DD} - {title}.{ext}" so both
# the publish date and title can be recovered offline without a network call.
VIDEO_ID_LEN = 11
DATE_LEN = 10  # YYYY-MM-DD
# offsets into the stem: "{id} - {date} - {title}"
DATE_START = VIDEO_ID_LEN + 3       # 14
DATE_END = DATE_START + DATE_LEN    # 24
TITLE_START = DATE_END + 3          # 27
WHISPER_LINES_KEY = "segments"


def dump_episode(doc):
    """Pretty-print top-level fields, one compact transcript line per item."""
    non_line = [(k, v) for k, v in doc.items() if k != "lines"]
    has_lines = "lines" in doc
    parts = ["{"]
    for i, (k, v) in enumerate(non_line):
        comma = "," if i < len(non_line) - 1 or has_lines else ""
        parts.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    if has_lines:
        parts.append('  "lines": [')
        doc_lines = doc["lines"]
        for i, line in enumerate(doc_lines):
            comma = "," if i < len(doc_lines) - 1 else ""
            parts.append(f"    {json.dumps(line, ensure_ascii=False)}{comma}")
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
    return audio_path.stem[TITLE_START:]


def publish_date_from_audio(audio_path):
    return audio_path.stem[DATE_START:DATE_END]


class Command(BaseCommand):
    help = "Download all audio in transcript_todos.jsonl, then transcribe each one"

    def add_arguments(self, parser):
        parser.add_argument(
            "--local-only",
            action="store_true",
            help="Skip downloads; only transcribe entries whose audio is already cached",
        )
        parser.add_argument(
            "--download-only",
            action="store_true",
            help="Download audio for all todo entries but skip transcription",
        )

    def handle(self, *args, **options):
        local_only = options["local_only"]
        download_only = options["download_only"]
        data_dir = settings.PIPELINE_DATA_DIR
        todo_path = data_dir / "transcript_todos.jsonl"
        history_path = data_dir / "scrape_history.jsonl"
        inbox_path = data_dir / "1_transcript_inbox"
        archive_path = data_dir / "transcript_archive"
        audio_dir = data_dir / "audio"
        inbox_path.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        archive_path.mkdir(parents=True, exist_ok=True)

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
                try:
                    title, publish_date = fetch_episode_meta(video_id)
                except yt_dlp.utils.DownloadError as e:
                    self.stdout.write(self.style.WARNING(f"  [{video_id}] skipped: {e}"))
                    continue
                publish_dates[video_id] = publish_date
                episode_url = f"https://www.youtube.com/watch?v={video_id}"
                ydl_opts = {
                    "format": "bestaudio/best",
                    "outtmpl": str(audio_dir / f"{video_id} - {publish_date} - {title}.%(ext)s"),
                    "quiet": True,
                    "no_warnings": True,
                }
                self.stdout.write(f"  [{video_id}] downloading \"{title}\" ({publish_date})...")
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([episode_url])
                except yt_dlp.utils.DownloadError as e:
                    self.stdout.write(self.style.WARNING(f"  [{video_id}] skipped: {e}"))
                    continue
                self.stdout.write(f"  [{video_id}] done")
            self.stdout.write("Phase 1 complete.\n")

        if download_only:
            self.stdout.write("--download-only: skipping transcription.")
            return

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
                publish_dates[video_id] = publish_date_from_audio(audio_path)
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

            transcript_lines = result[WHISPER_LINES_KEY]
            meta = {
                "type": "episode_meta",
                "video_id": video_id,
                "episode_title": episode_title,
                "episode_url": episode_url,
                "publish_date": publish_date,
            }

            archive_doc = {
                **meta,
                "lines": [
                    {
                        "line_number": i,
                        "text": line["text"].strip(),
                        "start": line["start"],
                        "duration": line["end"] - line["start"],
                    }
                    for i, line in enumerate(transcript_lines, start=1)
                ],
            }
            archive_file = archive_path / f"{video_id}.json"
            archive_file.write_text(dump_episode(archive_doc), encoding="utf-8")
            self.stdout.write(f"[{video_id}] Archived to {archive_file}")

            inbox_doc = {
                **meta,
                "lines": [
                    {
                        "line_number": i,
                        "text": line["text"].strip(),
                        "start": int(line["start"]),
                    }
                    for i, line in enumerate(transcript_lines, start=1)
                ],
            }
            inbox_file = inbox_path / f"{video_id}.json"
            inbox_file.write_text(dump_episode(inbox_doc), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"[{video_id}] Saved {len(transcript_lines)} lines to {inbox_file}"))

            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({**entry, "episode_title": episode_title}) + "\n")

            # Remove this entry from the todo file immediately after processing
            remaining_lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
            remaining_lines = [l for l in remaining_lines if json.loads(l)["video_id"] != video_id]
            todo_path.write_text(("\n".join(remaining_lines) + "\n") if remaining_lines else "")

        self.stdout.write(self.style.SUCCESS("\nAll done."))

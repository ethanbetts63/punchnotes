import json

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.import_utils.transcript_windows import write_inbox_transcript_windows

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


def find_audio(audio_dir, video_id):
    """Return the audio Path for a video_id, or None if not cached."""
    matches = list(audio_dir.glob(f"{video_id} - *.*"))
    return matches[0] if matches else None


def title_from_audio(audio_path):
    return audio_path.stem[TITLE_START:]


def publish_date_from_audio(audio_path):
    return audio_path.stem[DATE_START:DATE_END]


class Command(BaseCommand):
    help = "Transcribe audio from pipeline/data/0_audio_inbox for transcript_todos.jsonl entries"

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR
        todo_path = data_dir / "transcript_todos.jsonl"
        history_path = data_dir / "scrape_history.jsonl"
        inbox_path = data_dir / "1_transcript_inbox"
        archive_path = data_dir / "transcript_archive"
        audio_dir = data_dir / "0_audio_inbox"
        inbox_path.mkdir(parents=True, exist_ok=True)
        audio_dir.mkdir(parents=True, exist_ok=True)
        archive_path.mkdir(parents=True, exist_ok=True)

        lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
        if not lines:
            self.stdout.write("No entries in todo file.")
            return

        entries = [json.loads(l) for l in lines]

        to_process = [(e, find_audio(audio_dir, e["video_id"])) for e in entries]
        to_process = [(e, p) for e, p in to_process if p is not None]
        skipped = len(entries) - len(to_process)
        if skipped:
            self.stdout.write(f"Skipping {skipped} entries with no audio in {audio_dir}.")
        self.stdout.write(f"Transcribing {len(to_process)} entries...")

        import whisper

        model = whisper.load_model("small.en")

        for entry, audio_path in to_process:
            video_id = entry["video_id"]
            episode_title = title_from_audio(audio_path)
            episode_url = f"https://www.youtube.com/watch?v={video_id}"
            publish_date = publish_date_from_audio(audio_path)

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
            inbox_files = write_inbox_transcript_windows(inbox_doc, inbox_path, overlap=25)
            self.stdout.write(
                self.style.SUCCESS(
                    f"[{video_id}] Saved {len(inbox_files)} inbox transcript window(s)"
                )
            )

            with open(history_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({**entry, "episode_title": episode_title}) + "\n")

            # Remove this entry from the todo file immediately after processing
            remaining_lines = [l for l in todo_path.read_text().splitlines() if l.strip()]
            remaining_lines = [l for l in remaining_lines if json.loads(l)["video_id"] != video_id]
            todo_path.write_text(("\n".join(remaining_lines) + "\n") if remaining_lines else "")

        self.stdout.write(self.style.SUCCESS("\nAll done."))

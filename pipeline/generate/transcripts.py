import json
import shutil

from django.conf import settings

from pipeline.utils.transcript_windows import write_inbox_transcript_windows
from pipeline.log import Log


WHISPER_LINES_KEY = "segments"


def _dump_episode(doc: dict) -> str:
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


def _audio_files(audio_dir):
    return sorted(
        path for path in audio_dir.iterdir()
        if path.is_file() and path.suffix != ".part"
    )


def _parse_audio_filename(audio_path):
    parts = audio_path.stem.split(" - ", 2)
    if len(parts) != 3:
        return audio_path.stem[:11], None, audio_path.stem
    return parts[0], parts[1], parts[2]


def _archive_audio(audio_path, archive_dir):
    target = archive_dir / audio_path.name
    if target.exists():
        stem = audio_path.stem
        suffix = audio_path.suffix
        i = 2
        while target.exists():
            target = archive_dir / f"{stem} ({i}){suffix}"
            i += 1
    shutil.move(str(audio_path), target)
    return target


def generate_transcripts(options: dict, log: Log | None = None) -> None:
    import whisper

    log = log or Log()
    data_dir = settings.PIPELINE_DATA_DIR
    audio_dir = data_dir / "0_audio_inbox"
    audio_archive_dir = data_dir / "audio_archive"
    history_path = data_dir / "scrape_history.jsonl"
    inbox_path = data_dir / "1_transcript_inbox"
    archive_path = data_dir / "transcript_archive"
    audio_dir.mkdir(parents=True, exist_ok=True)
    audio_archive_dir.mkdir(parents=True, exist_ok=True)
    inbox_path.mkdir(parents=True, exist_ok=True)
    archive_path.mkdir(parents=True, exist_ok=True)

    files = _audio_files(audio_dir)
    limit = options.get("limit")
    if limit is not None:
        files = files[:limit]
    if not files:
        log(f"No complete audio files in {audio_dir}.")
        return

    log(f"Generating transcripts for {len(files)} audio file(s)...")
    model = whisper.load_model("small.en")
    generated = skipped = failed = 0

    for audio_path in files:
        video_id, publish_date, episode_title = _parse_audio_filename(audio_path)
        episode_url = f"https://www.youtube.com/watch?v={video_id}"
        archive_file = archive_path / f"{video_id}.json"

        if archive_file.exists():
            skipped += 1
            archived_audio = _archive_audio(audio_path, audio_archive_dir)
            log(f"[{video_id}] transcript already exists; archived audio to {archived_audio}")
            continue

        log(f"\n[{video_id}] Title: {episode_title}")
        log(f"[{video_id}] Transcribing with Whisper small.en...")
        try:
            result = model.transcribe(
                str(audio_path),
                language="en",
                fp16=False,
                verbose=True,
                condition_on_previous_text=False,
                suppress_tokens=[],
                beam_size=1,
            )
        except Exception as e:
            failed += 1
            log.error(f"[{video_id}] failed: {e}")
            continue

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
        archive_file.write_text(_dump_episode(archive_doc), encoding="utf-8")
        log(f"[{video_id}] Archived transcript to {archive_file}")

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
        log.success(f"[{video_id}] Saved {len(inbox_files)} inbox transcript window(s)")

        with history_path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {"video_id": video_id, "episode_title": episode_title, "audio_file": audio_path.name},
                    ensure_ascii=False,
                    separators=(",", ":"),
                ) + "\n"
            )

        archived_audio = _archive_audio(audio_path, audio_archive_dir)
        log(f"[{video_id}] Archived audio to {archived_audio}")
        generated += 1

    log.success(f"\nDone. {generated} generated, {skipped} skipped, {failed} failed.")

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yt_dlp
from django.conf import settings

from pipeline.log import Log


PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLy4mvfOQOs8Aw527rECOiIwvqXn525c8s"
EPISODE_NUMBER_PATTERN = re.compile(r"#\s*(\d+)")


def _parse_upload_date(raw: str | None) -> str | None:
    if raw and len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


def _episode_number(title: str) -> int | None:
    match = EPISODE_NUMBER_PATTERN.search(title)
    return int(match.group(1)) if match else None


def _record_from_entry(entry: dict, mode: str) -> dict:
    video_id = entry["id"]
    title = entry.get("title", "")
    return {
        "type": "episode",
        "fetch_mode": mode,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "episode_number": _episode_number(title),
        "episode_title": title,
        "episode_url": f"https://www.youtube.com/watch?v={video_id}",
        "duration_seconds": entry.get("duration"),
        "published_at": _parse_upload_date(entry.get("upload_date")),
    }


def _output_path(mode: str) -> Path:
    filename = "full_kt_episodes.jsonl" if mode == "full" else "basic_kt_episodes.jsonl"
    return settings.PIPELINE_DATA_DIR / filename


def _seen_video_ids(path: Path) -> set[str]:
    seen: set[str] = set()
    if not path or not path.exists():
        return seen
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                video_id = json.loads(line).get("video_id")
            except json.JSONDecodeError:
                continue
            if video_id:
                seen.add(video_id)
    return seen


def fetch_episode_metadata(mode: str, log: Log) -> Path:
    output_path = _output_path(mode)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seen_video_ids = _seen_video_ids(output_path)

    log(f"Scanning playlist ({mode})...")
    flat_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
    with yt_dlp.YoutubeDL(flat_opts) as ydl:
        info = ydl.extract_info(PLAYLIST_URL, download=False)

    entries = [e for e in info.get("entries", []) if e.get("id")]
    if not entries:
        raise RuntimeError("No playlist entries found.")

    log(f"  {len(entries)} entries found")
    log(f"  resuming {output_path}")
    log(f"  {len(seen_video_ids)} existing record(s) will be skipped")

    written = skipped = full_failed = 0
    video_opts = {"quiet": True, "no_warnings": True}
    with output_path.open("a", encoding="utf-8") as out:
        for i, entry in enumerate(entries, 1):
            record = _record_from_entry(entry, mode)
            video_id = record["video_id"]

            if video_id in seen_video_ids:
                skipped += 1
                continue

            if mode == "full":
                log(f"  [{i}/{len(entries)}] {video_id} - fetching video details")
                try:
                    with yt_dlp.YoutubeDL(video_opts) as ydl:
                        video_info = ydl.extract_info(record["episode_url"], download=False)
                    detailed_title = video_info.get("title") or record["episode_title"]
                    record.update({
                        "episode_number": _episode_number(detailed_title),
                        "episode_title": detailed_title,
                        "duration_seconds": video_info.get("duration") or record["duration_seconds"],
                        "published_at": _parse_upload_date(video_info.get("upload_date")) or record["published_at"],
                        "view_count": video_info.get("view_count"),
                        "like_count": video_info.get("like_count"),
                        "comment_count": video_info.get("comment_count"),
                    })
                except Exception as e:
                    full_failed += 1
                    record["detail_error"] = str(e)
                    log.error(f"    failed: {e}")
            else:
                log(f"  [{i}/{len(entries)}] {video_id}")

            out.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            out.flush()
            written += 1
            seen_video_ids.add(video_id)

    log(f"  {written} record(s) written")
    log(f"  {skipped} existing record(s) skipped")
    if mode == "full":
        log(f"  {full_failed} detail fetch(es) failed")
    log.success(f"Done: {output_path}")
    return output_path


def generate_ep_meta(options: dict, log: Log) -> None:
    mode = "full" if options.get("full", True) else "basic"
    output_path = fetch_episode_metadata(mode, log)

    outbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    dest = outbox_dir / output_path.name
    shutil.copy2(output_path, dest)
    log(f"Copied to {dest}")

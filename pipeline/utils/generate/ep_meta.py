import json
import re
from datetime import datetime, timezone

import yt_dlp
from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log


EPISODE_NUMBER_PATTERN = re.compile(r"#\s*(\d+)")


def _parse_upload_date(raw: str | None) -> str | None:
    if raw and len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return None


def _episode_number(title: str) -> int | None:
    match = EPISODE_NUMBER_PATTERN.search(title)
    return int(match.group(1)) if match else None


def _scrape_video(video_id: str) -> dict:
    url = f"https://www.youtube.com/watch?v={video_id}"
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    title = info.get("title", "")
    return {
        "type": "episode",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "video_id": video_id,
        "episode_number": _episode_number(title),
        "episode_title": title,
        "episode_url": url,
        "duration_seconds": info.get("duration"),
        "published_at": _parse_upload_date(info.get("upload_date")),
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "comment_count": info.get("comment_count"),
    }


def _report_result(video_id: str, status: str, error: str | None = None) -> None:
    payload = {"video_id": video_id, "status": status}
    if error:
        payload["error"] = error
    pipeline_session().post(server_url("/api/pipeline/video-scrape-result/"), json=payload)


def generate_ep_meta(options: dict, log: Log) -> None:
    video_id = options.get("video")

    if video_id:
        queue = [{"video_id": video_id}]
    else:
        log("Fetching scrape queue from server...")
        resp = pipeline_session().get(server_url("/api/pipeline/videos-to-scrape/"))
        queue = json_or_empty(resp).get("videos", [])
        if not queue:
            log("No videos queued for scraping.")
            return
        log(f"  {len(queue)} video(s) to scrape")

    outbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outbox_path = outbox_dir / f"ep_meta_{ts}.jsonl"
    archive_path = settings.PIPELINE_DATA_DIR / "kt_ep_archive.jsonl"

    succeeded = failed = 0
    with outbox_path.open("w", encoding="utf-8") as out, \
         archive_path.open("a", encoding="utf-8") as archive:
        for entry in queue:
            vid = entry.get("video_id") or entry
            log(f"  [{vid}] scraping...")
            try:
                record = _scrape_video(vid)
                line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
                out.write(line)
                out.flush()
                archive.write(line)
                archive.flush()
                if not video_id:
                    _report_result(vid, "success")
                log.success(f"  [{vid}] {record['episode_title']}")
                succeeded += 1
            except Exception as e:
                if not video_id:
                    _report_result(vid, "failed", str(e))
                log.error(f"  [{vid}] failed: {e}")
                failed += 1

    if succeeded == 0:
        outbox_path.unlink(missing_ok=True)
        log("No records written.")
    else:
        log.success(f"\nDone. {succeeded} scraped, {failed} failed. Written to {outbox_path.name}")

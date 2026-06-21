import json
import re

from django.conf import settings

from pipeline.log import Log
from pipeline.models import Video


EPISODE_NUMBER_PATTERN = re.compile(r"#\s*(\d+)")

FIELD_MAP = {
    "episode_number": "number",
    "episode_title": "title",
    "episode_url": "url",
    "duration_seconds": "duration_seconds",
    "published_at": "date",
    "view_count": "view_count",
    "like_count": "like_count",
    "comment_count": "comment_count",
}


def _view_like_ratio(view_count: int | None, like_count: int | None) -> float | None:
    if not view_count or like_count is None or like_count <= 0:
        return None
    return view_count / like_count


def _episode_number(title: str | None) -> int | None:
    if not title:
        return None
    match = EPISODE_NUMBER_PATTERN.search(title)
    return int(match.group(1)) if match else None


def ingest_ep_meta_jsonl(jsonl_text: str) -> dict:
    created = updated = failed = 0
    errors = []
    for line_number, line in enumerate(jsonl_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        video_id = None
        try:
            data = json.loads(line)
            video_id = data["video_id"]
            defaults = {
                model_field: data[source_field]
                for source_field, model_field in FIELD_MAP.items()
                if source_field in data and data[source_field] is not None
            }
            if "url" not in defaults:
                defaults["url"] = f"https://www.youtube.com/watch?v={video_id}"
            if "title" not in defaults:
                defaults["title"] = data.get("title") or video_id
            if "number" not in defaults:
                parsed = _episode_number(defaults.get("title"))
                if parsed is not None:
                    defaults["number"] = parsed
            if "guests" in data:
                defaults["guests"] = [guest for guest in data.get("guests") or [] if guest]
            view_count = defaults.get("view_count")
            like_count = defaults.get("like_count")
            if "view_count" in defaults or "like_count" in defaults:
                defaults["view_like_ratio"] = _view_like_ratio(view_count, like_count)
            _, was_created = Video.objects.update_or_create(video_id=video_id, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception as exc:
            failed += 1
            if len(errors) < 25:
                errors.append({
                    "line": line_number,
                    "video_id": video_id,
                    "error": f"{type(exc).__name__}: {exc}",
                })
    return {"created": created, "updated": updated, "failed": failed, "errors": errors}


def run_update_ep_meta(log: Log) -> None:
    path = settings.PIPELINE_DATA_DIR / "kt_ep_archive.jsonl"
    if not path.exists():
        log("kt_ep_archive.jsonl not found.")
        return
    result = ingest_ep_meta_jsonl(path.read_text(encoding="utf-8"))
    for error in result.get("errors", []):
        video = f" [{error['video_id']}]" if error.get("video_id") else ""
        log.error(f"  line {error['line']}{video}: {error['error']}")
    if result["failed"] > len(result.get("errors", [])):
        hidden = result["failed"] - len(result.get("errors", []))
        log.error(f"  ... {hidden} more failure(s) not shown")
    log.success(f"Done. {result['created']} created, {result['updated']} updated, {result['failed']} failed.")

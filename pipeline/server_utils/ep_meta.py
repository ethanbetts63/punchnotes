import json
import re
import shutil
from pathlib import Path

from django.conf import settings

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


def _episode_number(title: str | None) -> int | None:
    if not title:
        return None
    match = EPISODE_NUMBER_PATTERN.search(title)
    return int(match.group(1)) if match else None


def ingest_ep_meta_jsonl(jsonl_text: str) -> dict:
    """Upsert Video rows from JSONL text. Returns created/updated/failed counts."""
    created = updated = failed = 0

    for line in jsonl_text.splitlines():
        line = line.strip()
        if not line:
            continue
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

            _, was_created = Video.objects.update_or_create(video_id=video_id, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1
        except Exception:
            failed += 1

    return {"created": created, "updated": updated, "failed": failed}


def run_update_ep_meta(stdout=None, style=None) -> None:
    inbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_inbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "ep_meta_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(inbox_dir.glob("*.jsonl")) if inbox_dir.exists() else []
    if not files:
        if stdout:
            stdout.write("No files in ep_meta_inbox/")
        return

    total = {"created": 0, "updated": 0, "failed": 0}
    for path in files:
        result = ingest_ep_meta_jsonl(path.read_text(encoding="utf-8"))
        for k in total:
            total[k] += result[k]
        shutil.move(str(path), archive_dir / path.name)
        if stdout:
            stdout.write(f"  {path.name}: {result}")

    if stdout:
        stdout.write(style.SUCCESS(f"Done. {total}") if style else f"Done. {total}")

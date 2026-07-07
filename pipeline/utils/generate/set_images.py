import tempfile
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings

from pipeline.utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_set_images(options: dict, log: Log) -> None:
    from pipeline.scripts.grab_set_image import default_output_path, download_clip, grab_frame, youtube_url

    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/missing-set-images/"))
    resp.raise_for_status()
    missing = resp.json().get("sets", [])

    if not missing:
        log("No missing set images.")
        return

    log(f"{len(missing)} set(s) need images. Scraping...")
    outbox_dir = settings.PIPELINE_DATA_DIR / "set_images_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    offset = options.get("offset", 30)
    limit = options.get("limit")
    fetched = failed = 0

    for entry in missing:
        if limit is not None and fetched >= limit:
            break

        capture_seconds = entry["start_seconds"] + offset
        output_path = default_output_path(
            entry["video_id"], capture_seconds,
            entry["start_seconds"], entry["comedian_name"],
        )
        args = SimpleNamespace(
            video_id=entry["video_id"], url=None,
            start_seconds=entry["start_seconds"],
            comic_name=entry["comedian_name"], timestamp=entry["start_seconds"],
            offset=offset, clip_duration=options.get("clip_duration", 0.05),
            width=options.get("width", 480), quality=options.get("quality", 4),
            cookies_from_browser=options.get("cookies_from_browser"),
            cookies=options.get("cookies"),
        )
        try:
            half_clip = args.clip_duration / 2
            clip_start = max(capture_seconds - half_clip, 0)
            with tempfile.TemporaryDirectory(prefix="punchnotes_frame_") as tmp:
                clip_path = download_clip(youtube_url(video_id=entry["video_id"]), args, clip_start, clip_start + args.clip_duration, Path(tmp))
                grab_frame(clip_path, capture_seconds - clip_start, outbox_dir / output_path.name, args.width, args.quality)
            fetched += 1
            log(f"  Captured {output_path.name}")
        except Exception as exc:
            failed += 1
            log.warning(f"  Failed {entry['video_id']}: {exc}")

    log(f"Done. {fetched} captured, {failed} failed.")

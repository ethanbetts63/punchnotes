import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_set_images(options: dict, log: Log | None = None) -> None:
    from pipeline.scripts.grab_set_image import default_output_path, download_clip, grab_frame, youtube_url

    log = log or Log()
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
            entry["episode_number"], entry["set_number"], entry["comedian_name"],
        )
        args = SimpleNamespace(
            video_id=entry["video_id"], url=None,
            episode_number=entry["episode_number"], set_number=entry["set_number"],
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


def upload_set_images(options: dict, log: Log | None = None) -> None:
    log = log or Log()
    outbox_dir = settings.PIPELINE_DATA_DIR / "set_images_outbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p for p in outbox_dir.glob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ) if outbox_dir.exists() else []

    if not files:
        log(f"No images in {outbox_dir.name}/")
        return

    session = pipeline_session()
    imported = failed = 0

    for path in files:
        with open(path, "rb") as f:
            resp = session.post(
                server_url("/api/pipeline/set-images/"),
                files={"image": (path.name, f, "image/jpeg")},
            )
        result = resp.json() if resp.content else {}
        if resp.status_code in (200, 202):
            shutil.move(str(path), archive_dir / path.name)
            imported += 1
            log(f"  {path.name}: queued")
        else:
            failed += 1
            log.error(f"  {path.name}: {result.get('error') or resp.text}")

    log(f"Done. {imported} uploaded, {failed} failed.")

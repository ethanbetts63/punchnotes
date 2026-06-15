import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url


def generate_set_images(options: dict, stdout=None, style=None) -> None:
    """Get the missing-images list from the server, then scrape each locally."""
    from pipeline.scripts.grab_set_image import (
        default_output_path,
        download_clip,
        grab_frame,
        youtube_url,
    )

    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/missing-set-images/"))
    resp.raise_for_status()
    missing = resp.json().get("sets", [])

    if not missing:
        if stdout:
            stdout.write("No missing set images.")
        return

    if stdout:
        stdout.write(f"{len(missing)} set(s) need images. Scraping...")

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
            entry["video_id"],
            capture_seconds,
            entry["episode_number"],
            entry["set_number"],
            entry["comedian_name"],
        )
        dest = outbox_dir / output_path.name

        args = SimpleNamespace(
            video_id=entry["video_id"],
            url=None,
            episode_number=entry["episode_number"],
            set_number=entry["set_number"],
            comic_name=entry["comedian_name"],
            timestamp=entry["start_seconds"],
            offset=offset,
            clip_duration=options.get("clip_duration", 0.05),
            width=options.get("width", 480),
            quality=options.get("quality", 4),
            cookies_from_browser=options.get("cookies_from_browser"),
            cookies=options.get("cookies"),
        )

        try:
            half_clip = args.clip_duration / 2
            clip_start = max(capture_seconds - half_clip, 0)
            clip_end = capture_seconds + half_clip
            relative_seconds = capture_seconds - clip_start
            with tempfile.TemporaryDirectory(prefix="punchnotes_frame_") as tmp:
                clip_path = download_clip(youtube_url(video_id=entry["video_id"]), args, clip_start, clip_end, Path(tmp))
                grab_frame(clip_path, relative_seconds, dest, args.width, args.quality)
            fetched += 1
            if stdout:
                stdout.write(f"  Captured {dest.name}")
        except Exception as exc:
            failed += 1
            if stdout:
                stdout.write(style.WARNING(f"  Failed {entry['video_id']}: {exc}") if style else f"  Failed: {exc}")

    if stdout:
        stdout.write(f"Done. {fetched} captured, {failed} failed.")


def upload_set_images(options: dict, stdout=None, style=None) -> None:
    outbox_dir = settings.PIPELINE_DATA_DIR / "set_images_outbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        p for p in outbox_dir.glob("*")
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    ) if outbox_dir.exists() else []

    if not files:
        if stdout:
            stdout.write("No images in set_images_outbox/")
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
            if stdout:
                stdout.write(f"  {path.name}: queued")
        else:
            failed += 1
            error = result.get("error") or resp.text
            if stdout:
                stdout.write(style.ERROR(f"  {path.name}: {error}") if style else f"  {path.name}: {error}")

    if stdout:
        stdout.write(f"Done. {imported} uploaded, {failed} failed.")

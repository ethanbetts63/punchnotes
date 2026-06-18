import shutil
from pathlib import Path

from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log

BATCH_SIZE = 100


def _upload_batch(session, paths: list[Path], log: Log) -> list[Path]:
    files = [("images", (p.name, p.open("rb"), "image/jpeg")) for p in paths]
    try:
        resp = session.post(server_url("/api/pipeline/set-images-batch/"), files=files)
    finally:
        for _, (_, fh, _) in files:
            fh.close()

    result = json_or_empty(resp)
    if resp.status_code in (200, 202):
        return paths

    log.error(f"Batch upload failed [{resp.status_code}] - {result.get('error') or resp.text}")
    return []


def upload_set_images(options: dict, log: Log) -> None:
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
    uploaded = failed = 0

    for i in range(0, len(files), BATCH_SIZE):
        batch = files[i:i + BATCH_SIZE]
        log(f"Uploading batch {i // BATCH_SIZE + 1} ({len(batch)} images)...")
        succeeded = _upload_batch(session, batch, log)
        for path in succeeded:
            shutil.move(str(path), archive_dir / path.name)
        uploaded += len(succeeded)
        failed += len(batch) - len(succeeded)

    log(f"Done. {uploaded} uploaded, {failed} failed.")

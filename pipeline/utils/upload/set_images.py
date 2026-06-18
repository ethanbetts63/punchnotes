import shutil

from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log


def upload_set_images(options: dict, log: Log) -> None:
    outbox_dir = settings.PIPELINE_DATA_DIR / "set_images_outbox"
    archive_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "set_images_archive"
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
        result = json_or_empty(resp)
        if resp.status_code in (200, 202):
            shutil.move(str(path), archive_dir / path.name)
            imported += 1
            log(f"  {path.name}: queued")
        else:
            failed += 1
            log.error(f"  {path.name}: {result.get('error') or resp.text}")

    log(f"Done. {imported} uploaded, {failed} failed.")

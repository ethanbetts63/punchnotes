import shutil
import tempfile
import zipfile
from pathlib import Path

from django.conf import settings

from pipeline.log import Log
from pipeline.utils.http import json_or_empty, pipeline_session, server_url


def upload_annotated_files(paths: list[Path], log: Log) -> bool:
    session = pipeline_session()

    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_path = Path(tmp_dir) / "annotated_sets.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                archive.write(path, arcname=path.name)

        with archive_path.open("rb") as archive_file:
            resp = session.post(
                server_url("/api/pipeline/annotated-set-batch/"),
                files={"archive": ("annotated_sets.zip", archive_file, "application/zip")},
            )

    result = json_or_empty(resp)

    if resp.status_code in (200, 202):
        received = result.get("received", len(paths))
        log.success(f"Uploaded {received} annotated set file(s).")
        return True

    log.error(f"Batch upload failed [{resp.status_code}] - {result.get('error') or resp.text}")
    return False


def upload_annotated(options: dict, log: Log) -> None:
    archive_dir = settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    if options.get("file"):
        paths = [Path(options["file"])]
    else:
        source_dir = Path(options["dir"]) if options.get("dir") else settings.PIPELINE_DATA_DIR / "2_set_inbox"
        paths = sorted(source_dir.glob("*.json"))

    if not paths:
        log("No files to upload.")
        return

    if upload_annotated_files(paths, log):
        for path in paths:
            shutil.move(str(path), archive_dir / path.name)
        log(f"\n{len(paths)} uploaded, 0 failed.")
    else:
        log(f"\n0 uploaded, {len(paths)} failed.")

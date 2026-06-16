import json
import shutil
from pathlib import Path

from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log


def upload_annotated_file(path: Path, log: Log, defer_refresh: bool = False) -> bool:
    session = pipeline_session()
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    params = {"defer_refresh": "1"} if defer_refresh else {}
    resp = session.post(server_url("/api/pipeline/annotated-set/"), json=data, params=params)
    result = json_or_empty(resp)

    if resp.status_code == 200:
        comedian = result.get("comedian", "?")
        lines = result.get("lines", "?")
        bits = result.get("bits", "?")
        log.success(f"  {path.name}: {comedian} — {lines} lines, {bits} bits")
        return True

    log.error(f"  {path.name}: FAILED — {result.get('error') or resp.text}")
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

    batch = len(paths) > 1
    succeeded = failed = 0
    for path in paths:
        if upload_annotated_file(path, log, defer_refresh=batch):
            shutil.move(str(path), archive_dir / path.name)
            succeeded += 1
        else:
            failed += 1

    if batch and succeeded > 0:
        log("Refreshing stats...")
        session = pipeline_session()
        resp = session.post(server_url("/api/pipeline/refresh-stats/"))
        if resp.status_code == 200:
            log.success("Stats refreshed.")
        else:
            log.warning(f"Stats refresh failed: {resp.text}")

    log(f"\n{succeeded} uploaded, {failed} failed.")

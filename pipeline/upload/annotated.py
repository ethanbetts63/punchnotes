import json
import shutil
from pathlib import Path

from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log


def upload_annotated_file(path: Path, log: Log) -> bool:
    session = pipeline_session()
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    resp = session.post(server_url("/api/pipeline/annotated-set/"), json=data)
    result = json_or_empty(resp)

    if resp.status_code == 200:
        comedian = result.get("comedian", "?")
        lines = result.get("lines", "?")
        bits = result.get("bits", "?")
        log.success(f"  {path.name}: {comedian} — {lines} lines, {bits} bits")
        return True

    log.error(f"  {path.name}: FAILED — {result.get('error') or resp.text}")
    return False


def upload_annotated(options: dict, log: Log | None = None) -> None:
    log = log or Log()
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

    succeeded = failed = 0
    for path in paths:
        if upload_annotated_file(path, log):
            shutil.move(str(path), archive_dir / path.name)
            succeeded += 1
        else:
            failed += 1

    log(f"\n{succeeded} uploaded, {failed} failed.")

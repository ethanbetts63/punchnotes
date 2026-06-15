import shutil
from pathlib import Path

import requests
from django.conf import settings

from pipeline.log import Log


def pipeline_session() -> requests.Session:
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {settings.PIPELINE_API_KEY}"
    return s


def server_url(path: str) -> str:
    base = settings.SERVER_BASE_URL.rstrip("/")
    return f"{base}{path}"


def json_or_empty(resp) -> dict:
    return resp.json() if resp.content else {}


def upload_jsonl_files(
    outbox_dir: Path,
    archive_dir: Path,
    endpoint_path: str,
    log: Log | None = None,
) -> None:
    """POST each *.jsonl file in outbox_dir to endpoint_path, archive on success."""
    log = log or Log()
    archive_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(outbox_dir.glob("*.jsonl")) if outbox_dir.exists() else []
    if not files:
        log(f"No files in {outbox_dir.name}/")
        return
    session = pipeline_session()
    for path in files:
        resp = session.post(
            server_url(endpoint_path),
            data=path.read_bytes(),
            headers={"Content-Type": "application/x-ndjson"},
        )
        result = json_or_empty(resp)
        if resp.status_code in (200, 202):
            shutil.move(str(path), archive_dir / path.name)
            log.success(f"  {path.name}: ok")
        else:
            log.error(f"  {path.name}: {result.get('error') or resp.text}")

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
    if not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        return {}


def upload_jsonl_files(
    outbox_dir: Path,
    archive_dir: Path,
    endpoint_path: str,
    log: Log,
) -> None:
    """POST each *.jsonl file in outbox_dir to endpoint_path, archive on success."""
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


def upload_jsonl_files_chunked(
    outbox_dir: Path,
    archive_dir: Path,
    endpoint_path: str,
    chunk_size: int,
    log: Log,
    move_to_archive: bool = True,
) -> None:
    """POST JSONL files in line chunks, archive the source only if all chunks upload."""
    if chunk_size < 1:
        raise ValueError("--chunk-size must be at least 1")

    archive_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(outbox_dir.glob("*.jsonl")) if outbox_dir.exists() else []
    if not files:
        log(f"No files in {outbox_dir.name}/")
        return

    session = pipeline_session()
    for path in files:
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines:
            shutil.move(str(path), archive_dir / path.name)
            log.success(f"  {path.name}: empty, archived")
            continue

        total_chunks = (len(lines) + chunk_size - 1) // chunk_size
        size_mb = path.stat().st_size / (1024 * 1024)
        log(f"  {path.name}: {len(lines)} lines, {total_chunks} chunk(s), {size_mb:.1f} MB")
        uploaded = 0
        failed = False
        for chunk_number, start in enumerate(range(0, len(lines), chunk_size), start=1):
            chunk = "\n".join(lines[start:start + chunk_size]) + "\n"
            log(f"  {path.name}: uploading chunk {chunk_number}/{total_chunks}...")
            resp = session.post(
                server_url(endpoint_path),
                data=chunk.encode("utf-8"),
                headers={"Content-Type": "application/x-ndjson"},
            )
            result = json_or_empty(resp)
            if resp.status_code not in (200, 202):
                log.error(
                    f"  {path.name}: chunk {chunk_number}/{total_chunks} failed: "
                    f"{result.get('error') or resp.text}"
                )
                failed = True
                break
            uploaded += 1
            log(f"  {path.name}: chunk {chunk_number}/{total_chunks} ok")

        if not failed:
            if move_to_archive:
                shutil.move(str(path), archive_dir / path.name)
            log.success(f"  {path.name}: ok ({uploaded} chunk(s))")

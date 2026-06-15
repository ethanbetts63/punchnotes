import shutil
from pathlib import Path

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url


def generate_ep_meta(options: dict, stdout=None, style=None) -> None:
    """Scrape episode metadata and write to ep_meta_outbox/."""
    from django.core.management import call_command

    outbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    mode = "--full" if options.get("full", True) else "--basic"
    call_command("fetch_episodes", mode)

    src = settings.PIPELINE_DATA_DIR / ("full_kt_episodes.jsonl" if mode == "--full" else "basic_kt_episodes.jsonl")
    if src.exists():
        dest = outbox_dir / src.name
        shutil.copy2(src, dest)
        if stdout:
            stdout.write(f"Written to {dest}")
    elif stdout:
        stdout.write(style.WARNING("fetch_episodes produced no output file.") if style else "No output file found.")


def upload_ep_meta(options: dict, stdout=None, style=None) -> None:
    outbox_dir = settings.PIPELINE_DATA_DIR / "ep_meta_outbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "ep_meta_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(outbox_dir.glob("*.jsonl")) if outbox_dir.exists() else []
    if not files:
        if stdout:
            stdout.write("No files in ep_meta_outbox/")
        return

    session = pipeline_session()
    for path in files:
        resp = session.post(
            server_url("/api/pipeline/ep-meta/"),
            data=path.read_bytes(),
            headers={"Content-Type": "application/x-ndjson"},
        )
        result = resp.json() if resp.content else {}
        if resp.status_code in (200, 202):
            shutil.move(str(path), archive_dir / path.name)
            if stdout:
                stdout.write(style.SUCCESS(f"  {path.name}: queued") if style else f"  {path.name}: queued")
        else:
            error = result.get("error") or resp.text
            if stdout:
                stdout.write(style.ERROR(f"  {path.name}: {error}") if style else f"  {path.name}: {error}")

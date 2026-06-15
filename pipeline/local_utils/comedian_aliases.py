import json
import shutil
from pathlib import Path

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url


def generate_comedian_aliases(stdout=None, style=None) -> None:
    """Fetch similar_comedian_candidates.json from the server and save locally."""
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/comedian-candidates/"))
    resp.raise_for_status()
    dest = settings.PIPELINE_DATA_DIR / "similar_comedian_candidates.json"
    dest.write_text(resp.text, encoding="utf-8")
    count = resp.json().get("candidate_count", "?")
    if stdout:
        stdout.write(f"Fetched {count} candidate pair(s) -> {dest}")


def upload_comedian_aliases(stdout=None, style=None) -> None:
    """Upload comedian_name_relationships.json to the server."""
    outbox_dir = settings.PIPELINE_DATA_DIR / "comedian_aliases_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    src = settings.PIPELINE_DATA_DIR / "comedian_name_relationships.json"
    if not src.exists():
        if stdout:
            stdout.write(
                style.ERROR("comedian_name_relationships.json not found.") if style
                else "comedian_name_relationships.json not found."
            )
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    session = pipeline_session()
    resp = session.post(server_url("/api/pipeline/comedian-aliases/"), json=data)
    result = resp.json() if resp.content else {}

    if resp.status_code == 200:
        if stdout:
            stdout.write(style.SUCCESS("Comedian aliases uploaded.") if style else "Comedian aliases uploaded.")
    else:
        error = result.get("error") or resp.text
        if stdout:
            stdout.write(style.ERROR(f"Failed: {error}") if style else f"Failed: {error}")

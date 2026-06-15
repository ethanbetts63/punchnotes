import json

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_comedian_aliases(log: Log | None = None) -> None:
    log = log or Log()
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/comedian-candidates/"))
    resp.raise_for_status()
    dest = settings.PIPELINE_DATA_DIR / "similar_comedian_candidates.json"
    dest.write_text(resp.text, encoding="utf-8")
    count = resp.json().get("candidate_count", "?")
    log(f"Fetched {count} candidate pair(s) -> {dest}")


def upload_comedian_aliases(log: Log | None = None) -> None:
    log = log or Log()
    src = settings.PIPELINE_DATA_DIR / "comedian_name_relationships.json"
    if not src.exists():
        log.error("comedian_name_relationships.json not found.")
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    session = pipeline_session()
    resp = session.post(server_url("/api/pipeline/comedian-aliases/"), json=data)
    result = resp.json() if resp.content else {}

    if resp.status_code == 200:
        log.success("Comedian aliases uploaded.")
    else:
        log.error(f"Failed: {result.get('error') or resp.text}")

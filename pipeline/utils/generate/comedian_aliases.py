from django.conf import settings

from pipeline.utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_comedian_aliases(log: Log) -> None:
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/comedian-candidates/"))
    resp.raise_for_status()
    dest = settings.PIPELINE_DATA_DIR / "similar_comedian_candidates.json"
    dest.write_text(resp.text, encoding="utf-8")
    count = resp.json().get("candidate_count", "?")
    log(f"Fetched {count} candidate pair(s) -> {dest}")

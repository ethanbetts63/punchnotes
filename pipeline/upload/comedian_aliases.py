import json

from django.conf import settings

from pipeline.utils.http import json_or_empty, pipeline_session, server_url
from pipeline.log import Log


def upload_comedian_aliases(log: Log | None = None) -> None:
    log = log or Log()
    src = settings.PIPELINE_DATA_DIR / "comedian_name_relationships.json"
    if not src.exists():
        log.error("comedian_name_relationships.json not found.")
        return

    data = json.loads(src.read_text(encoding="utf-8"))
    session = pipeline_session()
    resp = session.post(server_url("/api/pipeline/comedian-aliases/"), json=data)
    result = json_or_empty(resp)

    if resp.status_code == 200:
        log.success("Comedian aliases uploaded.")
    else:
        log.error(f"Failed: {result.get('error') or resp.text}")

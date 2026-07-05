import json

import pytest
from django.test import override_settings


pytestmark = pytest.mark.django_db


def test_unsegmented_beat_segments_view_returns_segments(api_client, full_set):
    full_set["bit"].bit_id = "bit_001"
    full_set["bit"].save(update_fields=["bit_id"])
    full_set["beat"].beat_id = "bit_001_beat_001"
    full_set["beat"].save(update_fields=["beat_id"])

    resp = api_client.get("/api/pipeline/unsegmented-beat-segments/")

    assert resp.status_code == 200
    segments = resp.json()["segments"]
    assert len(segments) == 1
    assert segments[0]["key"].endswith(".seg001")


def test_segment_embeddings_view_writes_inbox_file(api_client, tmp_path):
    payload = json.dumps({"key": "ep700.set01.bit001.beat001.seg001", "embedding": [1.0, 2.0]}) + "\n"

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/segment-embeddings/",
            data=payload.encode("utf-8"),
            content_type="application/x-ndjson",
        )

    assert resp.status_code == 202
    files = list((tmp_path / "segment_embeddings_inbox").glob("*.jsonl"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8") == payload

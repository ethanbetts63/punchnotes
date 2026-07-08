import json

import numpy as np
import pytest


pytestmark = pytest.mark.django_db


def _unit(*values):
    vector = np.asarray(values, dtype=np.float32)
    return vector / np.linalg.norm(vector)


@pytest.fixture(autouse=True)
def _clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


def _post(client, text):
    return client.post(
        "/api/killtony/plagiarism/",
        data=json.dumps({"text": text}),
        content_type="application/json",
    )


def test_plagiarism_returns_beat_with_matched_segments(client, full_set, monkeypatch):
    from pipeline.models import BeatSegment

    beat = full_set["beat"]
    BeatSegment.objects.create(
        beat=beat, ordinal=1, text="I used to be an astronaut.",
        line_start=1, line_end=1, embedding=_unit(1, 0).tolist(),
    )

    monkeypatch.setattr(
        "api.views.plagiarism.embed_texts",
        lambda texts: [_unit(1, 0) for _ in texts],
    )

    resp = _post(client, "I used to be an astronaut for a living.")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) == 1

    match = results[0]
    assert match["comedian"] == "Casey Rocket"
    assert match["similarity"] == pytest.approx(1.0)
    # Full non-fluff beat rendered for line-by-line display
    assert [l["line_number"] for l in match["lines"]] == [1, 3]
    assert all(l["label"] != "fluff" for l in match["lines"])
    # Matched segment carries the line range to highlight
    assert match["matched_segments"][0]["line_start"] == 1
    assert match["matched_segments"][0]["line_end"] == 1
    assert match["matched_segments"][0]["similarity"] == pytest.approx(1.0)


def test_plagiarism_omits_beats_below_threshold(client, full_set, monkeypatch):
    from pipeline.models import BeatSegment

    BeatSegment.objects.create(
        beat=full_set["beat"], ordinal=1, text="unrelated",
        line_start=1, line_end=1, embedding=_unit(0, 1).tolist(),
    )
    monkeypatch.setattr(
        "api.views.plagiarism.embed_texts",
        lambda texts: [_unit(1, 0) for _ in texts],
    )

    resp = _post(client, "Something completely different from the corpus.")
    assert resp.status_code == 200
    assert resp.json()["results"] == []

import numpy as np
import pytest
from django.core.cache import cache

from api import hf_embeddings
from api.hf_embeddings import embed_texts


@pytest.fixture(autouse=True)
def _clear_cache():
    cache.clear()
    yield
    cache.clear()


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        pass


def _install_fake_post(monkeypatch, respond):
    calls = []

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(json["inputs"])
        return respond(json["inputs"])

    monkeypatch.setattr(hf_embeddings.requests, "post", fake_post)
    return calls


def test_multiple_texts_are_one_request_in_order(monkeypatch):
    calls = _install_fake_post(
        monkeypatch,
        lambda inputs: FakeResponse([[float(i + 1), 0.0] for i in range(len(inputs))]),
    )

    vectors = embed_texts(["first", "second", "third"])

    assert calls == [["first", "second", "third"]]
    # Order preserved, and every vector is unit-normalized
    assert all(np.linalg.norm(v) == pytest.approx(1.0) for v in vectors)
    assert vectors[0].tolist() == [1.0, 0.0]


def test_cached_texts_are_not_resent(monkeypatch):
    calls = _install_fake_post(
        monkeypatch,
        lambda inputs: FakeResponse([[1.0, 0.0] for _ in inputs]),
    )

    embed_texts(["warm", "cold"])
    embed_texts(["warm", "cold", "new"])

    assert calls == [["warm", "cold"], ["new"]]


def test_fully_cached_batch_makes_no_request(monkeypatch):
    calls = _install_fake_post(monkeypatch, lambda inputs: FakeResponse([[1.0, 0.0] for _ in inputs]))

    embed_texts(["only"])
    assert len(calls) == 1

    embed_texts(["only"])
    assert len(calls) == 1


def test_mismatched_response_length_raises(monkeypatch):
    _install_fake_post(monkeypatch, lambda inputs: FakeResponse([[1.0, 0.0]]))

    with pytest.raises(ValueError, match="Expected 2 embeddings"):
        embed_texts(["a", "b"])


def test_token_level_output_falls_back_to_first_row(monkeypatch):
    # Defensive: some pipeline configs return [tokens x dims] per input.
    _install_fake_post(
        monkeypatch,
        lambda inputs: FakeResponse([[[3.0, 0.0], [0.0, 1.0]]]),
    )

    (vector,) = embed_texts(["a"])
    assert vector.tolist() == [1.0, 0.0]

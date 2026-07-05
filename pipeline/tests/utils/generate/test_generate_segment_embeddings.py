import json

import numpy as np

from pipeline.utils.generate import segment_embeddings


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self._payload = payload

    def get(self, url, params=None):
        return FakeResponse(self._payload)


class FakeModel:
    def encode(self, texts, batch_size, show_progress_bar):
        return np.array([[float(len(t)), 0.0] for t in texts])


def test_generate_segment_embeddings_writes_outbox_file(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    segments_payload = {
        "segments": [{"id": 1, "key": "ep1.set01.bit001.beat001.seg001", "text": "hello world"}],
        "next_cursor": 1,
        "built_beats": 1,
        "has_more": False,
    }
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession(segments_payload))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", lambda name, **kwargs: FakeModel())

    log = CapturingLog()
    segment_embeddings.generate_segment_embeddings({}, log)

    files = list((tmp_path / "segment_embeddings_outbox").glob("*.jsonl"))
    assert len(files) == 1
    line = json.loads(files[0].read_text(encoding="utf-8").splitlines()[0])
    assert line["key"] == "ep1.set01.bit001.beat001.seg001"
    assert line["embedding"] == [11.0, 0.0]
    assert "Written 1 segment embeddings" in log.messages[-1]


def test_generate_segment_embeddings_no_segments_logs_and_returns(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession({
        "segments": [],
        "next_cursor": 0,
        "built_beats": 0,
        "has_more": False,
    }))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    log = CapturingLog()
    segment_embeddings.generate_segment_embeddings({}, log)

    assert log.messages == [
        "Fetching beat segments from https://example.test/api/pipeline/unsegmented-beat-segments/ in batches of 1000...",
        "Fetching segment batch 1 after id 0...",
        "Fetched 0 segment(s), built segments for 0 beat(s); has_more=False.",
        "No beat segments need embeddings.",
    ]
    assert not (tmp_path / "segment_embeddings_outbox").exists()


def test_generate_segment_embeddings_rejects_invalid_batch_size(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    segments_payload = {"segments": [{"id": 1, "key": "ep1.set01.bit001.beat001.seg001", "text": "hi"}]}
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession(segments_payload))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    import pytest
    with pytest.raises(ValueError, match="--batch-size must be at least 1"):
        segment_embeddings.generate_segment_embeddings({"batch_size": 0}, CapturingLog())

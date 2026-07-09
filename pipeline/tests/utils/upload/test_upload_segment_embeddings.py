from pipeline.utils.upload import segment_embeddings


class CapturingLog:
    def __call__(self, msg):
        pass

    def success(self, msg):
        pass

    def error(self, msg):
        pass


def test_upload_segment_embeddings_uses_correct_dirs_and_endpoint(monkeypatch, settings, tmp_path):
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(segment_embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"

    segment_embeddings.upload_segment_embeddings({}, CapturingLog())

    assert captured["outbox_dir"] == tmp_path / "data" / "segment_embeddings_outbox"
    assert captured["endpoint_path"] == "/api/pipeline/segment-embeddings/"
    assert "archive_dir" not in captured
    assert "move_to_archive" not in captured


def test_upload_segment_embeddings_ignores_archive_flag(monkeypatch, settings, tmp_path):
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(segment_embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"

    segment_embeddings.upload_segment_embeddings({"archive": True}, CapturingLog())

    # Segment embeddings are never archived, so --archive has no source to read from.
    assert captured["outbox_dir"] == tmp_path / "data" / "segment_embeddings_outbox"

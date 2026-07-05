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
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"

    segment_embeddings.upload_segment_embeddings({}, CapturingLog())

    assert captured["outbox_dir"] == tmp_path / "data" / "segment_embeddings_outbox"
    assert captured["archive_dir"] == tmp_path / "private" / "segment_embeddings_archive"
    assert captured["endpoint_path"] == "/api/pipeline/segment-embeddings/"
    assert captured["move_to_archive"] is True


def test_upload_segment_embeddings_archive_mode_reads_private_archive(monkeypatch, settings, tmp_path):
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(segment_embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"

    segment_embeddings.upload_segment_embeddings({"archive": True}, CapturingLog())

    archive = tmp_path / "private" / "segment_embeddings_archive"
    assert captured["outbox_dir"] == archive
    assert captured["archive_dir"] == archive
    assert captured["move_to_archive"] is False

from pipeline.utils import http
from pipeline.utils.upload import embeddings


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


class FakeResponse:
    status_code = 202
    content = b'{"status":"queued"}'
    text = '{"status":"queued"}'

    def json(self):
        return {"status": "queued"}


class FakeSession:
    def __init__(self):
        self.payloads = []

    def post(self, url, data, headers):
        self.payloads.append((url, data.decode("utf-8"), headers))
        return FakeResponse()


def test_upload_jsonl_files_chunked_archives_after_all_chunks(tmp_path, monkeypatch):
    outbox = tmp_path / "embeddings_outbox"
    archive = tmp_path / "embeddings_archive"
    outbox.mkdir()
    source = outbox / "embeddings.jsonl"
    source.write_text("one\ntwo\nthree\n", encoding="utf-8")
    session = FakeSession()
    log = CapturingLog()

    monkeypatch.setattr(http, "pipeline_session", lambda: session)
    monkeypatch.setattr(http, "server_url", lambda path: f"https://example.test{path}")

    http.upload_jsonl_files_chunked(
        outbox_dir=outbox,
        archive_dir=archive,
        endpoint_path="/api/pipeline/embeddings/",
        chunk_size=2,
        log=log,
    )

    assert [payload for _, payload, _ in session.payloads] == ["one\ntwo\n", "three\n"]
    assert not source.exists()
    assert (archive / "embeddings.jsonl").exists()
    assert "3 lines, 2 chunk(s)" in log.messages[0]
    assert "uploading chunk 1/2" in log.messages[1]
    assert "chunk 2/2 ok" in log.messages[-2]
    assert log.messages[-1] == "  embeddings.jsonl: ok (2 chunk(s))"


def test_upload_jsonl_files_chunked_can_leave_archive_files_in_place(tmp_path, monkeypatch):
    archive = tmp_path / "embeddings_archive"
    archive.mkdir()
    source = archive / "embeddings.jsonl"
    source.write_text("one\n", encoding="utf-8")
    session = FakeSession()
    log = CapturingLog()

    monkeypatch.setattr(http, "pipeline_session", lambda: session)
    monkeypatch.setattr(http, "server_url", lambda path: f"https://example.test{path}")

    http.upload_jsonl_files_chunked(
        outbox_dir=archive,
        archive_dir=archive,
        endpoint_path="/api/pipeline/embeddings/",
        chunk_size=2,
        log=log,
        move_to_archive=False,
    )

    assert [payload for _, payload, _ in session.payloads] == ["one\n"]
    assert source.exists()
    assert "1 lines, 1 chunk(s)" in log.messages[0]
    assert "uploading chunk 1/1" in log.messages[1]
    assert log.messages[-1] == "  embeddings.jsonl: ok (1 chunk(s))"


def test_upload_embeddings_archive_reads_private_archive_without_moving(tmp_path, settings, monkeypatch):
    archive = tmp_path / "private" / "embeddings_archive"
    archive.mkdir(parents=True)
    source = archive / "embeddings.jsonl"
    source.write_text("one\n", encoding="utf-8")
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"

    embeddings.upload_embeddings({"archive": True}, CapturingLog())

    assert captured["outbox_dir"] == archive
    assert captured["archive_dir"] == archive
    assert captured["move_to_archive"] is False

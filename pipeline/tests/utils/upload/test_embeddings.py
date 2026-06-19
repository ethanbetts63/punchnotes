from pipeline.utils import http


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
    assert log.messages[-1] == "  embeddings.jsonl: ok (2 chunk(s))"

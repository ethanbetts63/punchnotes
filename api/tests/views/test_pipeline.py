import json
import zipfile
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings


pytestmark = pytest.mark.django_db


def _write_jsonl(path, records):
    path.write_text(
        "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in records),
        encoding="utf-8",
    )


def _zip_json_files(files):
    payload = BytesIO()
    with zipfile.ZipFile(payload, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, json.dumps(data))
    return SimpleUploadedFile("annotated.zip", payload.getvalue(), content_type="application/zip")


def test_annotated_set_batch_upload_writes_inbox_files(api_client, tmp_path):
    data = {
        "set_id": "set-1",
        "video_id": "abc123",
        "comedian_name": "Test Comic",
        "start_seconds": 42,
        "lines": [],
    }
    archive = _zip_json_files({"source.json": data})

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/annotated-set-batch/",
            {"archive": archive},
        )

    assert resp.status_code == 202
    assert resp.json()["received"] == 1
    written = tmp_path / "annotated_set_inbox" / "abc123_test_comic_42s.json"
    assert json.loads(written.read_text(encoding="utf-8"))["comedian_name"] == "Test Comic"


def test_annotated_set_batch_upload_keeps_repeat_comedian_sets_distinct(api_client, tmp_path):
    first = {
        "video_id": "abc123",
        "comedian_name": "Test Comic",
        "start_seconds": 42,
        "lines": [],
    }
    second = {
        "video_id": "abc123",
        "comedian_name": "Test Comic",
        "start_seconds": 84,
        "lines": [],
    }
    archive = _zip_json_files({"first.json": first, "second.json": second})

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/annotated-set-batch/",
            {"archive": archive},
        )

    assert resp.status_code == 202
    assert sorted(resp.json()["files"]) == [
        "abc123_test_comic_42s.json",
        "abc123_test_comic_84s.json",
    ]
    inbox = tmp_path / "annotated_set_inbox"
    assert (inbox / "abc123_test_comic_42s.json").exists()
    assert (inbox / "abc123_test_comic_84s.json").exists()


def test_annotated_set_batch_upload_rejects_invalid_annotation(api_client, tmp_path):
    archive = _zip_json_files({"bad.json": {"video_id": "abc123", "comedian_name": "Test Comic", "lines": "bad"}})

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/annotated-set-batch/",
            {"archive": archive},
        )

    assert resp.status_code == 400
    assert resp.json()["files"][0]["file"] == "bad.json"
    assert "lines must be a JSON array" in resp.json()["files"][0]["error"]
    assert not (tmp_path / "annotated_set_inbox").exists()


def test_annotated_set_batch_upload_rejects_unsafe_zip_path(api_client, tmp_path):
    archive = _zip_json_files({"../source.json": {"video_id": "abc123", "comedian_name": "Test Comic"}})

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/annotated-set-batch/",
            {"archive": archive},
        )

    assert resp.status_code == 400
    assert not (tmp_path / "annotated_set_inbox").exists()


def test_videos_to_scrape_returns_empty_when_no_file(api_client, tmp_path):
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.get("/api/pipeline/videos-to-scrape/")
    assert resp.status_code == 200
    assert resp.json()["videos"] == []


def test_videos_to_scrape_returns_all_when_none_known(api_client, tmp_path):
    _write_jsonl(tmp_path / "videos_to_scrape.jsonl", [{"video_id": "aaa"}, {"video_id": "bbb"}])
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.get("/api/pipeline/videos-to-scrape/")
    assert resp.status_code == 200
    assert [v["video_id"] for v in resp.json()["videos"]] == ["aaa", "bbb"]


def test_videos_to_scrape_filters_video_ids_in_db(api_client, tmp_path):
    from pipeline.models import Video
    Video.objects.create(video_id="aaa", title="KT #1", url="https://example.com/1")
    _write_jsonl(tmp_path / "videos_to_scrape.jsonl", [{"video_id": "aaa"}, {"video_id": "bbb"}])

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.get("/api/pipeline/videos-to-scrape/")

    assert [v["video_id"] for v in resp.json()["videos"]] == ["bbb"]


def test_videos_to_scrape_filters_video_ids_in_history(api_client, tmp_path):
    _write_jsonl(tmp_path / "videos_to_scrape.jsonl", [{"video_id": "aaa"}, {"video_id": "bbb"}])
    _write_jsonl(tmp_path / "video_scrape_history.jsonl", [{"video_id": "aaa", "status": "failed"}])

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.get("/api/pipeline/videos-to-scrape/")

    assert [v["video_id"] for v in resp.json()["videos"]] == ["bbb"]


def test_videos_to_scrape_rewrites_file_removing_known(api_client, tmp_path):
    from pipeline.models import Video
    Video.objects.create(video_id="aaa", title="KT #1", url="https://example.com/1")
    _write_jsonl(tmp_path / "videos_to_scrape.jsonl", [{"video_id": "aaa"}, {"video_id": "bbb"}])

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        api_client.get("/api/pipeline/videos-to-scrape/")

    remaining = [json.loads(l) for l in (tmp_path / "videos_to_scrape.jsonl").read_text().splitlines() if l.strip()]
    assert [r["video_id"] for r in remaining] == ["bbb"]


def test_video_scrape_result_records_success(api_client, tmp_path):
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/video-scrape-result/",
            data=json.dumps({"video_id": "aaa", "status": "success"}),
            content_type="application/json",
        )
    assert resp.status_code == 200
    history = [json.loads(l) for l in (tmp_path / "video_scrape_history.jsonl").read_text().splitlines()]
    assert history[0]["video_id"] == "aaa"
    assert history[0]["status"] == "success"


def test_video_scrape_result_records_failure_with_error(api_client, tmp_path):
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/video-scrape-result/",
            data=json.dumps({"video_id": "bbb", "status": "failed", "error": "age restricted"}),
            content_type="application/json",
        )
    assert resp.status_code == 200
    history = [json.loads(l) for l in (tmp_path / "video_scrape_history.jsonl").read_text().splitlines()]
    assert history[0]["error"] == "age restricted"


def test_video_scrape_result_rejects_invalid_status(api_client, tmp_path):
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/video-scrape-result/",
            data=json.dumps({"video_id": "aaa", "status": "pending"}),
            content_type="application/json",
        )
    assert resp.status_code == 400


def test_pipeline_endpoints_require_auth(client, tmp_path):
    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        assert client.get("/api/pipeline/videos-to-scrape/").status_code == 403
        assert client.post("/api/pipeline/video-scrape-result/").status_code == 403

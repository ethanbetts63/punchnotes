import json

import pytest

from pipeline.models import Video
from pipeline.utils.update.ep_meta import ingest_ep_meta_jsonl, run_update_ep_meta


pytestmark = pytest.mark.django_db


def test_ingest_ep_meta_imports_guests():
    payload = {
        "video_id": "pJtNBld3pcU",
        "episode_number": 190,
        "episode_title": "Kill Tony #190 - Doug Benson, Big Jay Oakerson & Dom Irrera",
        "episode_url": "https://www.youtube.com/watch?v=pJtNBld3pcU",
        "guests": ["Doug Benson", "Big Jay Oakerson", "Dom Irrera"],
    }

    result = ingest_ep_meta_jsonl(json.dumps(payload) + "\n")

    video = Video.objects.get(video_id="pJtNBld3pcU")
    assert result == {"created": 1, "updated": 0, "failed": 0, "errors": []}
    assert video.guests == [
        "Doug Benson",
        "Big Jay Oakerson",
        "Dom Irrera",
    ]


def test_ingest_ep_meta_sets_view_like_ratio():
    payload = {
        "video_id": "ratio123",
        "episode_title": "Kill Tony #701",
        "view_count": 10_000,
        "like_count": 500,
    }

    result = ingest_ep_meta_jsonl(json.dumps(payload) + "\n")

    video = Video.objects.get(video_id="ratio123")
    assert result == {"created": 1, "updated": 0, "failed": 0, "errors": []}
    assert video.view_like_ratio == 20


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def test_run_update_ep_meta_reports_failure_details(tmp_path, settings):
    archive = tmp_path / "kt_ep_archive.jsonl"
    archive.write_text('{"episode_title":"Missing video id"}\n', encoding="utf-8")
    settings.PIPELINE_DATA_DIR = tmp_path
    log = CapturingLog()

    run_update_ep_meta(log)

    assert "line 1" in log.messages[0]
    assert "KeyError" in log.messages[0]
    assert "video_id" in log.messages[0]
    assert log.messages[-1] == "Done. 0 created, 0 updated, 1 failed."

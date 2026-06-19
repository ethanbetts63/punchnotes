import json

import pytest

from pipeline.models import Video
from pipeline.utils.update.ep_meta import ingest_ep_meta_jsonl


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
    assert result == {"created": 1, "updated": 0, "failed": 0}
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
    assert result == {"created": 1, "updated": 0, "failed": 0}
    assert video.view_like_ratio == 20

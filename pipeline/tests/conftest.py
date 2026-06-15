import pytest


@pytest.fixture
def comedian(db):
    from pipeline.models import Comedian
    return Comedian.objects.create(name="Test Comic", slug="test-comic")


@pytest.fixture
def video(db):
    from pipeline.models import Video
    return Video.objects.create(video_id="abc123xyz01", title="KT #1", url="https://example.com")


@pytest.fixture
def standup_set(db, comedian, video):
    from pipeline.models import Set
    return Set.objects.create(video=video, comedian=comedian, set_number=1, start_seconds=0)

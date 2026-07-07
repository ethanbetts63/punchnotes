import pytest
from django.conf import settings


@pytest.fixture
def api_client():
    from django.test import Client
    client = Client()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {settings.PIPELINE_API_KEY}"
    return client


@pytest.fixture
def full_set(db):
    """Comedian + video + set + lines + bit + beat — the minimal complete data shape."""
    from pipeline.models import Beat, Bit, Comedian, Line, Set, Video

    comedian = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", set_count=1)
    video = Video.objects.create(
        video_id="abc123xyz01", number=700, title="Kill Tony #700",
        url="https://example.com/kt-700", set_count=1,
    )
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=60, bit_count=1)
    bit = Bit.objects.create(set=set_obj, bit_id="b1", line_start=1, line_end=3)
    beat = Beat.objects.create(
        bit=bit, beat_id="beat-1", line_start=1, line_end=3,
        premise="Rockets could be dreams.", joke_type="reframe",
    )
    Line.objects.bulk_create([
        Line(set=set_obj, line_number=1, label="setup", text="I used to be an astronaut.", start_seconds=60),
        Line(set=set_obj, line_number=2, label="fluff", text="Well not really.", start_seconds=61),
        Line(set=set_obj, line_number=3, label="punchline", text="I was a rocket scientist though.", start_seconds=62),
    ])
    return {"comedian": comedian, "video": video, "set": set_obj, "bit": bit, "beat": beat}

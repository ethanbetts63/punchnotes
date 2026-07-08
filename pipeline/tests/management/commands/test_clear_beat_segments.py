import pytest
from django.core.management import call_command

from pipeline.models import Beat, BeatSegment, Bit, Comedian, Set, Video


pytestmark = pytest.mark.django_db


def _make_beat():
    comedian = Comedian.objects.create(name="Comic", slug="comic")
    video = Video.objects.create(video_id="vid", number=1, title="ep", url="https://e/1")
    standup_set = Set.objects.create(video=video, comedian=comedian, start_seconds=10)
    bit = Bit.objects.create(set=standup_set, bit_id="bit_001", line_start=1, line_end=1)
    return Beat.objects.create(bit=bit, beat_id="bit_001_beat_001", line_start=1, line_end=1, joke_type="misdirect")


def test_clear_beat_segments_deletes_all_rows():
    beat = _make_beat()
    BeatSegment.objects.create(beat=beat, ordinal=1, text="a", line_start=1, line_end=1, embedding=[1.0])
    BeatSegment.objects.create(beat=beat, ordinal=2, text="b", line_start=1, line_end=1)

    call_command("clear_beat_segments")

    assert BeatSegment.objects.count() == 0


def test_clear_beat_segments_is_a_noop_when_empty():
    call_command("clear_beat_segments")
    assert BeatSegment.objects.count() == 0

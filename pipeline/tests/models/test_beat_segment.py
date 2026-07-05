import pytest
from django.db import IntegrityError


pytestmark = pytest.mark.django_db


def test_beat_segment_defaults_and_str(full_set):
    from pipeline.models import BeatSegment

    segment = BeatSegment.objects.create(
        beat=full_set["beat"],
        ordinal=1,
        text="I used to be an astronaut.",
        line_start=1,
        line_end=1,
    )

    assert segment.embedding == []
    assert str(segment) == f"{full_set['beat']} â€“ segment 1"
    assert full_set["beat"].segments.count() == 1


def test_beat_segment_ordinal_is_unique_per_beat(full_set):
    from pipeline.models import BeatSegment

    BeatSegment.objects.create(beat=full_set["beat"], ordinal=1, text="a", line_start=1, line_end=1)
    with pytest.raises(IntegrityError):
        BeatSegment.objects.create(beat=full_set["beat"], ordinal=1, text="b", line_start=2, line_end=2)

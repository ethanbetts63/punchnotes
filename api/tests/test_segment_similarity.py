import numpy as np
import pytest

from api.segment_similarity import find_similar_beats_by_segments
from pipeline.utils.vectors import pack_embedding


pytestmark = pytest.mark.django_db


def _unit(*values):
    vector = np.asarray(values, dtype=np.float32)
    return vector / np.linalg.norm(vector)


def _make_beat(slug, number, joke_type="misdirect"):
    from pipeline.models import Beat, Bit, Comedian, Set, Video

    comedian = Comedian.objects.create(name=slug, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", number=number, title=slug, url=f"https://e/{slug}")
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=10)
    bit = Bit.objects.create(set=set_obj, bit_id="bit_001", line_start=1, line_end=2)
    return Beat.objects.create(bit=bit, beat_id="bit_001_beat_001", line_start=1, line_end=2, joke_type=joke_type)


def test_ranks_beats_by_best_matching_segment():
    from pipeline.models import BeatSegment

    near = _make_beat("near", 1)
    far = _make_beat("far", 2)
    BeatSegment.objects.create(beat=near, ordinal=1, text="a", line_start=1, line_end=1, embedding=pack_embedding(_unit(1, 0)))
    BeatSegment.objects.create(beat=far, ordinal=1, text="b", line_start=1, line_end=1, embedding=pack_embedding(_unit(0, 1)))

    query = [_unit(1, 0)]
    results = find_similar_beats_by_segments(query, threshold=0.5)

    assert [entry["beat"].id for entry in results] == [near.id]
    assert results[0]["best"] == pytest.approx(1.0)


def test_collects_multiple_matched_segments_per_beat():
    from pipeline.models import BeatSegment

    beat = _make_beat("multi", 3)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="first", line_start=1, line_end=1, embedding=pack_embedding(_unit(1, 0)))
    BeatSegment.objects.create(beat=beat, ordinal=2, text="second", line_start=2, line_end=2, embedding=pack_embedding(_unit(0.9, 0.1)))
    BeatSegment.objects.create(beat=beat, ordinal=3, text="unrelated", line_start=2, line_end=2, embedding=pack_embedding(_unit(0, 1)))

    query = [_unit(1, 0)]
    results = find_similar_beats_by_segments(query, threshold=0.5)

    assert len(results) == 1
    matched_texts = [segment.text for segment, _ in results[0]["segments"]]
    assert matched_texts == ["first", "second"]  # sorted by score desc, "unrelated" below threshold


def test_takes_max_similarity_across_query_segments():
    from pipeline.models import BeatSegment

    beat = _make_beat("maxq", 4)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="seg", line_start=1, line_end=1, embedding=pack_embedding(_unit(0, 1)))

    query = [_unit(1, 0), _unit(0, 1)]
    results = find_similar_beats_by_segments(query, threshold=0.5)

    assert len(results) == 1
    assert results[0]["best"] == pytest.approx(1.0)


def test_empty_query_returns_nothing():
    _make_beat("none", 5)
    assert find_similar_beats_by_segments([]) == []

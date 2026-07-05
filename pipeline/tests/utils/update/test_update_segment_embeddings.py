import pytest

from pipeline.models import Beat, BeatSegment, Bit, Comedian, Line, Set, Video


pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number, video_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(
        video_id=f"vid-{slug}",
        number=video_number,
        title=f"Episode {slug}",
        url=f"https://example.com/{slug}",
    )
    return Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10))


def _make_beat(standup_set, bit_num, beat_num, line_start, line_end, joke_type="misdirect"):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit_{bit_num:03d}", line_start=line_start, line_end=line_end)
    return Beat.objects.create(
        bit=bit,
        beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
        line_start=line_start,
        line_end=line_end,
        joke_type=joke_type,
    )


def test_ensure_beat_segments_creates_rows_for_new_beats():
    from pipeline.utils.update.segment_embeddings import ensure_beat_segments

    standup_set = _make_set("Comic One", "comic-one", 1, 100)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="This is the punchline right here today.", start_seconds=1.0)

    ensure_beat_segments([beat])

    segments = list(beat.segments.order_by("ordinal"))
    assert len(segments) == 1
    assert segments[0].ordinal == 1
    assert segments[0].text == "This is the punchline right here today."


def test_ensure_beat_segments_skips_beats_that_already_have_segments():
    from pipeline.utils.update.segment_embeddings import ensure_beat_segments

    standup_set = _make_set("Comic One", "comic-one-2", 1, 101)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Original stored text.", start_seconds=1.0)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="manually seeded", line_start=1, line_end=1)

    ensure_beat_segments([beat])

    assert list(beat.segments.values_list("text", flat=True)) == ["manually seeded"]


def test_unembedded_beat_segments_builds_and_returns_missing_keys():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-3", 2, 102)
    beat = _make_beat(standup_set, 3, 4, 5, 5)
    Line.objects.create(set=standup_set, line_number=5, label="punchline", text="A single punchline segment.", start_seconds=1.0)

    result = unembedded_beat_segments()

    assert result == [{"key": "ep102.set02.bit003.beat004.seg001", "text": "A single punchline segment."}]
    assert Beat.objects.get(id=beat.id).segments.count() == 1


def test_unembedded_beat_segments_excludes_beats_without_joke_type():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-4", 1, 103)
    _make_beat(standup_set, 1, 1, 1, 1, joke_type="")
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Untyped beat text.", start_seconds=1.0)

    assert unembedded_beat_segments() == []


def test_unembedded_beat_segments_excludes_already_embedded_segments():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-5", 1, 104)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Already embedded text.", start_seconds=1.0)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="Already embedded text.", line_start=1, line_end=1, embedding=[1.0, 0.0])

    assert unembedded_beat_segments() == []


def test_ingest_segment_embeddings_stores_by_key():
    from pipeline.utils.update.segment_embeddings import ingest_segment_embeddings

    standup_set = _make_set("Comic One", "comic-one-6", 2, 105)
    beat = _make_beat(standup_set, 3, 4, 1, 1)
    segment = BeatSegment.objects.create(beat=beat, ordinal=1, text="text", line_start=1, line_end=1)

    result = ingest_segment_embeddings([
        {"key": "ep105.set02.bit003.beat004.seg001", "embedding": [1.0, 2.0]},
    ])

    segment.refresh_from_db()
    assert result == {"stored": 1, "not_found": 0, "invalid_key": 0}
    assert segment.embedding == [1.0, 2.0]


def test_ingest_segment_embeddings_reports_not_found_and_invalid_key():
    from pipeline.utils.update.segment_embeddings import ingest_segment_embeddings

    result = ingest_segment_embeddings([
        {"key": "ep999.set01.bit001.beat001.seg001", "embedding": [1.0]},
        {"key": "not-a-real-key", "embedding": [1.0]},
    ])

    assert result == {"stored": 0, "not_found": 1, "invalid_key": 1}

import pytest

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video
from pipeline.utils.update.embeddings import _parse_key, ingest_embeddings, unembedded_beats


pytestmark = pytest.mark.django_db


def _make_beat(start_seconds=100.0):
    comedian = Comedian.objects.create(name="Test Comic", slug="test-comic")
    video = Video.objects.create(video_id="vid0001", number=1, title="KT #1", url="https://example.com/1")
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=start_seconds)
    bit = Bit.objects.create(set=set_obj, bit_id="bit_001", line_start=1, line_end=3)
    beat = Beat.objects.create(
        bit=bit, beat_id="bit_001_beat_001", line_start=1, line_end=3,
        joke_type="reframe", embedding=[],
    )
    Line.objects.bulk_create([
        Line(set=set_obj, line_number=1, label="setup", text="setup", start_seconds=start_seconds),
        Line(set=set_obj, line_number=2, label="fluff", text="fluff", start_seconds=start_seconds + 1),
        Line(set=set_obj, line_number=3, label="punchline", text="punch", start_seconds=start_seconds + 2),
    ])
    return beat


def test_parse_key_extracts_start_seconds():
    assert _parse_key("ep1.ts100.bit001.beat001") == {
        "episode_number": 1,
        "start_seconds": 100,
        "bit_number": 1,
        "beat_number": 1,
    }


def test_parse_key_rejects_old_set_number_format():
    assert _parse_key("ep1.set01.bit001.beat001") is None


def test_unembedded_beats_key_uses_start_seconds():
    _make_beat(start_seconds=142.0)
    [entry] = unembedded_beats()
    assert entry["key"] == "ep1.ts142.bit001.beat001"


def test_ingest_embeddings_matches_by_truncated_start_seconds():
    beat = _make_beat(start_seconds=142.7)
    result = ingest_embeddings([{"key": "ep1.ts142.bit001.beat001", "embedding": [0.1, 0.2]}])

    beat.refresh_from_db()
    assert result == {"stored": 1, "not_found": 0, "invalid_key": 0}
    assert beat.embedding == [0.1, 0.2]


def test_ingest_embeddings_not_found_for_wrong_start_seconds():
    _make_beat(start_seconds=142.0)
    result = ingest_embeddings([{"key": "ep1.ts999.bit001.beat001", "embedding": [0.1]}])
    assert result == {"stored": 0, "not_found": 1, "invalid_key": 0}

import json

import pytest
from django.core.management import call_command
from django.test import override_settings

from pipeline.models import Beat, BeatSegment, Bit, Comedian, Set, Video
from pipeline.utils.vectors import pack_embedding


pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", title=f"Episode {slug}", url=f"https://example.com/{slug}")
    return Set.objects.create(video=video, comedian=comedian, start_seconds=float(set_number * 10))


def _make_beat(standup_set, beat_id, joke_type="misdirect"):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit-{beat_id}", line_start=1, line_end=1)
    return Beat.objects.create(bit=bit, beat_id=beat_id, line_start=1, line_end=1, joke_type=joke_type)


def test_report_matches_segments_across_different_comedians(tmp_path):
    set_a = _make_set("Comic One", "comic-one", 1)
    set_b = _make_set("Comic Two", "comic-two", 1)
    beat_a = _make_beat(set_a, "a")
    beat_b = _make_beat(set_b, "b")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="the punchline text", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="the punchline text", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert payload["threshold"] == 0.70
    assert len(payload["pairs"]) == 1
    pair = payload["pairs"][0]
    assert pair["similarity"] == 1.0
    assert {pair["beat_a"]["comedian"], pair["beat_b"]["comedian"]} == {"Comic One", "Comic Two"}
    assert pair["beat_a"]["matched_segment"] == "the punchline text"


def test_report_matches_segments_across_different_joke_types(tmp_path):
    set_a = _make_set("Comic One", "comic-one-xtype", 1)
    set_b = _make_set("Comic Two", "comic-two-xtype", 1)
    beat_a = _make_beat(set_a, "a", joke_type="misdirect")
    beat_b = _make_beat(set_b, "b", joke_type="reframe")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="reused joke", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="reused joke", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert len(payload["pairs"]) == 1
    assert payload["pairs"][0]["similarity"] == 1.0


def test_report_does_not_match_segments_from_same_comedian(tmp_path):
    set_a = _make_set("Comic One", "comic-one-2", 1)
    beat_a = _make_beat(set_a, "a")
    beat_b = _make_beat(set_a, "b")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="text", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="text", line_start=1, line_end=1, embedding=pack_embedding([1.0, 0.0]))

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert payload["pairs"] == []


def test_report_takes_best_segment_pair_per_beat_pair(tmp_path):
    set_a = _make_set("Comic One", "comic-one-3", 1)
    set_b = _make_set("Comic Two", "comic-two-3", 1)
    beat_a = _make_beat(set_a, "a")
    beat_b = _make_beat(set_b, "b")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="unrelated setup", line_start=1, line_end=1, embedding=pack_embedding([0.0, 1.0]))
    BeatSegment.objects.create(beat=beat_a, ordinal=2, text="matching punchline", line_start=2, line_end=2, embedding=pack_embedding([1.0, 0.0]))
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="different setup", line_start=1, line_end=1, embedding=pack_embedding([0.0, -1.0]))
    BeatSegment.objects.create(beat=beat_b, ordinal=2, text="matching punchline", line_start=2, line_end=2, embedding=pack_embedding([1.0, 0.0]))

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert len(payload["pairs"]) == 1
    assert payload["pairs"][0]["similarity"] == 1.0
    assert payload["pairs"][0]["beat_a"]["matched_segment"] == "matching punchline"


def test_report_warns_when_no_embedded_segments_exist(tmp_path):
    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    assert not (tmp_path / "segment_embedding_similarity_report.json").exists()

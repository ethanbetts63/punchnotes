import json
from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings

from pipeline.management.commands.generate_embeddings_report import _build_beat_records, fetch_lines_for_beats
from pipeline.models import Beat, Bit, Comedian, Line, Set, Video


pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", title=f"Episode {slug}", url=f"https://example.com/{slug}")
    return Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10))


def _make_beat(standup_set, beat_id, line_start, line_end, premise, embedding):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit-{beat_id}", line_start=line_start, line_end=line_end)
    return Beat.objects.create(
        bit=bit, beat_id=beat_id, line_start=line_start, line_end=line_end,
        premise=premise, joke_type="misdirect", embedding=embedding,
    )


def test_fetch_lines_for_beats_uses_single_query(django_assert_num_queries):
    standup_set = _make_set("Comic One", "comic-one", 1)
    beat_a = _make_beat(standup_set, "a", 1, 2, "first premise", [1.0, 0.0])
    beat_b = _make_beat(standup_set, "b", 3, 4, "second premise", [1.0, 0.0])
    Line.objects.bulk_create([
        Line(set=standup_set, line_number=1, label="setup", text="setup a", start_seconds=1.0),
        Line(set=standup_set, line_number=2, label="punchline", text="punch a", start_seconds=2.0),
        Line(set=standup_set, line_number=3, label="setup", text="setup b", start_seconds=3.0),
        Line(set=standup_set, line_number=4, label="tag", text="tag b", start_seconds=4.0),
    ])

    records = _build_beat_records(Beat.objects.filter(id__in=[beat_a.id, beat_b.id]).select_related("bit__set__comedian"))

    with django_assert_num_queries(1):
        lines_by_beat = fetch_lines_for_beats(records)

    assert lines_by_beat[beat_a.id] == [{"label": "setup", "text": "setup a"}, {"label": "punchline", "text": "punch a"}]
    assert lines_by_beat[beat_b.id] == [{"label": "setup", "text": "setup b"}, {"label": "tag", "text": "tag b"}]


def test_command_writes_report_with_similar_pairs(tmp_path):
    set_a = _make_set("Comic One", "comic-one", 1)
    set_b = _make_set("Comic Two", "comic-two", 1)
    beat_a = _make_beat(set_a, "a", 1, 2, "premise a", [1.0, 0.0])
    beat_b = _make_beat(set_b, "b", 1, 2, "premise b", [1.0, 0.0])
    Line.objects.bulk_create([
        Line(set=set_a, line_number=1, label="setup", text="setup a", start_seconds=1.0),
        Line(set=set_a, line_number=2, label="punchline", text="punch a", start_seconds=2.0),
        Line(set=set_b, line_number=1, label="setup", text="setup b", start_seconds=1.0),
        Line(set=set_b, line_number=2, label="punchline", text="punch b", start_seconds=2.0),
    ])

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        call_command("generate_embeddings_report")

    payload = json.loads((tmp_path / "embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert "generated_at" in payload
    assert payload["threshold"] == 0.70
    assert len(payload["pairs"]) == 1
    pair = payload["pairs"][0]
    assert pair["similarity"] == 1.0
    assert {pair["beat_a"]["id"], pair["beat_b"]["id"]} == {beat_a.id, beat_b.id}

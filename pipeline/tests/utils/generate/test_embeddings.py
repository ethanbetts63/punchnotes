import pytest

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video
from pipeline.utils.beats import embedding_text, load_lines_by_set


pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", title=f"Episode {slug}", url=f"https://example.com/{slug}")
    return Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10))


def _make_beat(standup_set, beat_id, line_start, line_end):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit-{beat_id}", line_start=line_start, line_end=line_end)
    return Beat.objects.create(bit=bit, beat_id=beat_id, line_start=line_start, line_end=line_end, premise=f"premise {beat_id}", joke_type="misdirect")


def test_embedding_text_plain_format():
    standup_set = _make_set("Comic One", "comic-one", 1)
    beat = _make_beat(standup_set, "a", 1, 3)
    Line.objects.bulk_create([
        Line(set=standup_set, line_number=1, label="setup", text="setup one", start_seconds=1.0),
        Line(set=standup_set, line_number=2, label="setup", text="setup two", start_seconds=2.0),
        Line(set=standup_set, line_number=3, label="punchline", text="punch", start_seconds=3.0),
    ])

    assert embedding_text(beat) == "setup one setup two punch"


def test_embedding_text_structured_format():
    standup_set = _make_set("Comic One", "comic-one-2", 1)
    beat = _make_beat(standup_set, "a", 1, 3)
    Line.objects.bulk_create([
        Line(set=standup_set, line_number=1, label="setup", text="setup one", start_seconds=1.0),
        Line(set=standup_set, line_number=2, label="setup", text="setup two", start_seconds=2.0),
        Line(set=standup_set, line_number=3, label="punchline", text="punch", start_seconds=3.0),
    ])

    assert embedding_text(beat, text_format="structured") == "Setup: setup one setup two\nPunchline: punch"


def test_load_lines_by_set_batches_in_single_query(django_assert_num_queries):
    standup_set = _make_set("Comic One", "comic-one-3", 1)
    beat_a = _make_beat(standup_set, "a", 1, 2)
    beat_b = _make_beat(standup_set, "b", 3, 4)
    Line.objects.bulk_create([
        Line(set=standup_set, line_number=1, label="setup", text="setup one", start_seconds=1.0),
        Line(set=standup_set, line_number=2, label="punchline", text="punch one", start_seconds=2.0),
        Line(set=standup_set, line_number=3, label="setup", text="setup two", start_seconds=3.0),
        Line(set=standup_set, line_number=4, label="punchline", text="punch two", start_seconds=4.0),
    ])

    with django_assert_num_queries(1):
        lines_by_set = load_lines_by_set([beat_a, beat_b])

    assert embedding_text(beat_a, lines_by_set=lines_by_set) == "setup one punch one"
    assert embedding_text(beat_b, lines_by_set=lines_by_set, text_format="structured") == "Setup: setup two\nPunchline: punch two"

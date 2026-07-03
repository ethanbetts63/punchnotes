import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video
from pipeline.utils.beats_by_joke_type import (
    build_beat_slug,
    build_report,
    normalize_joke_type,
    resolve_comedian,
)

pytestmark = pytest.mark.django_db


def _make_set(video_number, set_number, comedian):
    video = Video.objects.create(
        video_id=f"vid{video_number}",
        number=video_number,
        title=f"Episode {video_number}",
        url=f"https://example.com/{video_number}",
    )
    return Set.objects.create(
        video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10)
    )


def _make_beat(standup_set, bit_num, beat_num, joke_type, premise, line_start, line_end):
    bit = Bit.objects.create(
        set=standup_set, bit_id=f"bit_{bit_num:03d}", line_start=line_start, line_end=line_end
    )
    return Beat.objects.create(
        bit=bit,
        beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
        line_start=line_start,
        line_end=line_end,
        premise=premise,
        joke_type=joke_type,
    )


def _give_joke_book(standup_set, size):
    standup_set.attributes = [f"{size}_joke_book"]
    standup_set.save(update_fields=["attributes"])


def test_resolve_comedian_by_slug():
    comedian = Comedian.objects.create(name="William Montgomery", slug="william-montgomery")
    assert resolve_comedian("william-montgomery") == comedian
    assert resolve_comedian("William Montgomery") == comedian


def test_resolve_comedian_missing_raises():
    with pytest.raises(CommandError):
        resolve_comedian("nobody-here")


def test_normalize_joke_type_accepts_plural_and_spaces():
    assert normalize_joke_type("analogies") == "analogy"
    assert normalize_joke_type("Double Meaning") == "double-meaning"
    assert normalize_joke_type("double_meaning") == "double-meaning"


def test_normalize_joke_type_rejects_unknown():
    with pytest.raises(CommandError):
        normalize_joke_type("puns")


def test_build_beat_slug_format():
    comedian = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket")
    standup_set = _make_set(15, 15, comedian)
    beat = _make_beat(standup_set, 1, 1, "analogy", "premise", 1, 3)
    assert build_beat_slug(beat) == "vid15-set15-casey-rocket?bit=001&beat=001"


def test_build_report_filters_by_comedian_and_joke_type():
    comedian_a = Comedian.objects.create(name="Comic A", slug="comic-a")
    comedian_b = Comedian.objects.create(name="Comic B", slug="comic-b")
    set_a = _make_set(1, 1, comedian_a)
    set_b = _make_set(2, 1, comedian_b)

    target = _make_beat(set_a, 1, 1, "analogy", "target premise", 1, 2)
    _make_beat(set_a, 2, 1, "misdirect", "wrong joke type", 3, 4)
    _make_beat(set_b, 1, 1, "analogy", "wrong comedian", 1, 2)

    Line.objects.bulk_create([
        Line(set=set_a, line_number=1, label="setup", text="setup line", start_seconds=1.0),
        Line(set=set_a, line_number=2, label="punchline", text="punch line", start_seconds=2.0),
        Line(set=set_a, line_number=3, label="setup", text="other setup", start_seconds=3.0),
        Line(set=set_a, line_number=4, label="punchline", text="other punch", start_seconds=4.0),
    ])

    report = build_report("analogy", comedian=comedian_a)

    assert len(report) == 1
    assert report[0]["slug"] == build_beat_slug(target)
    assert report[0]["premise"] == "target premise"
    assert report[0]["lines"] == ["setup line", "punch line"]


def test_build_report_filters_by_joke_book():
    comedian = Comedian.objects.create(name="Comic A", slug="comic-a")
    big_set = _make_set(1, 1, comedian)
    _give_joke_book(big_set, "large")
    small_set = _make_set(2, 1, comedian)
    _give_joke_book(small_set, "small")

    target = _make_beat(big_set, 1, 1, "analogy", "big book premise", 1, 1)
    _make_beat(small_set, 1, 1, "analogy", "small book premise", 1, 1)
    Line.objects.create(set=big_set, line_number=1, label="punchline", text="big book line", start_seconds=1.0)
    Line.objects.create(set=small_set, line_number=1, label="punchline", text="small book line", start_seconds=1.0)

    report = build_report("analogy", joke_book="large")

    assert len(report) == 1
    assert report[0]["slug"] == build_beat_slug(target)


def test_build_report_without_comedian_covers_everyone():
    comedian_a = Comedian.objects.create(name="Comic A", slug="comic-a")
    comedian_b = Comedian.objects.create(name="Comic B", slug="comic-b")
    set_a = _make_set(1, 1, comedian_a)
    set_b = _make_set(2, 1, comedian_b)
    _make_beat(set_a, 1, 1, "analogy", "premise a", 1, 1)
    _make_beat(set_b, 1, 1, "analogy", "premise b", 1, 1)
    Line.objects.create(set=set_a, line_number=1, label="punchline", text="line a", start_seconds=1.0)
    Line.objects.create(set=set_b, line_number=1, label="punchline", text="line b", start_seconds=1.0)

    report = build_report("analogy")

    assert {entry["comedian"] for entry in report} == {"Comic A", "Comic B"}


def test_command_writes_txt_file(tmp_path, settings):
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path
    comedian = Comedian.objects.create(name="Comic A", slug="comic-a")
    standup_set = _make_set(1, 1, comedian)
    _make_beat(standup_set, 1, 1, "analogy", "premise", 1, 2)
    Line.objects.bulk_create([
        Line(set=standup_set, line_number=1, label="setup", text="setup line", start_seconds=1.0),
        Line(set=standup_set, line_number=2, label="punchline", text="punch line", start_seconds=2.0),
    ])

    call_command("beats_by_joke_type", comedian="comic-a", joke_type="analogy")

    output_path = tmp_path / "beat_reports" / "analogy_comic-a.txt"
    content = output_path.read_text(encoding="utf-8")
    assert content == "vid1-set01-comic-a?bit=001&beat=001\nsetup line\npunch line\n"


def test_command_writes_json_file(tmp_path, settings):
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path
    comedian = Comedian.objects.create(name="Comic A", slug="comic-a")
    standup_set = _make_set(1, 1, comedian)
    _make_beat(standup_set, 1, 1, "analogy", "premise", 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="only line", start_seconds=1.0)

    call_command("beats_by_joke_type", comedian="comic-a", joke_type="analogy", format="json")

    output_path = tmp_path / "beat_reports" / "analogy_comic-a.json"
    import json
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["comedian"] == "Comic A"
    assert payload["joke_type"] == "analogy"
    assert payload["count"] == 1
    assert payload["beats"][0]["lines"] == ["only line"]


def test_command_without_comedian_scopes_to_joke_book(tmp_path, settings):
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path
    comedian = Comedian.objects.create(name="Comic A", slug="comic-a")
    big_set = _make_set(1, 1, comedian)
    _give_joke_book(big_set, "large")
    small_set = _make_set(2, 1, comedian)
    _give_joke_book(small_set, "small")
    _make_beat(big_set, 1, 1, "analogy", "big premise", 1, 1)
    _make_beat(small_set, 1, 1, "analogy", "small premise", 1, 1)
    Line.objects.create(set=big_set, line_number=1, label="punchline", text="big line", start_seconds=1.0)
    Line.objects.create(set=small_set, line_number=1, label="punchline", text="small line", start_seconds=1.0)

    call_command("beats_by_joke_type", joke_type="analogy", joke_book="large")

    output_path = tmp_path / "beat_reports" / "analogy_large-joke-book.txt"
    content = output_path.read_text(encoding="utf-8")
    assert "big line" in content
    assert "small line" not in content

import pytest

from api.beat_utils import beat_display_lines, beat_lines, describe_beat_lines
from api.views.search import text_score


# --- text_score (no DB) ---

def test_text_score_exact_match():
    assert text_score("casey", "Casey") == 100

def test_text_score_prefix_match():
    assert text_score("case", "Casey Rocket") == 80

def test_text_score_contains_match():
    assert text_score("rocket", "Casey Rocket") == 50

def test_text_score_no_match():
    assert text_score("dave", "Casey Rocket") == 0

def test_text_score_returns_best_across_multiple_values():
    assert text_score("casey", "unknown", "Casey") == 100

def test_text_score_ignores_none_values():
    assert text_score("casey", None, "Casey") == 100


# --- beat_lines + describe_beat_lines (DB needed) ---

pytestmark = pytest.mark.django_db


def test_beat_lines_returns_only_lines_in_range(full_set):
    beat = full_set["beat"]  # line_start=1, line_end=3
    lines = beat_lines(beat)
    assert [l.line_number for l in lines] == [1, 2, 3]


def test_beat_lines_excludes_lines_outside_range(full_set):
    from pipeline.models import Line
    beat = full_set["beat"]
    Line.objects.create(set=full_set["set"], line_number=4, label="fluff", text="Outside.", start_seconds=63)
    lines = beat_lines(beat)
    assert all(l.line_number <= 3 for l in lines)


def test_beat_display_lines_excludes_fluff_and_keeps_order(full_set):
    lines = beat_display_lines(full_set["beat"])
    assert [l["line_number"] for l in lines] == [1, 3]
    assert [l["label"] for l in lines] == ["setup", "punchline"]
    assert all(l["label"] != "fluff" for l in lines)


def test_describe_beat_lines_finds_punchline(full_set):
    result = describe_beat_lines(full_set["beat"])
    assert result["punchline"] == "I was a rocket scientist though."


def test_describe_beat_lines_collects_setup_lines(full_set):
    result = describe_beat_lines(full_set["beat"])
    assert result["setup_lines"] == ["I used to be an astronaut."]


def test_describe_beat_lines_finds_matched_line_by_query(full_set):
    result = describe_beat_lines(full_set["beat"], query="astronaut")
    assert result["matched_line"].text == "I used to be an astronaut."
    assert result["matched_line"].label == "setup"


def test_describe_beat_lines_no_match_on_fluff(full_set):
    result = describe_beat_lines(full_set["beat"], query="really")
    assert result["matched_line"] is None


def test_describe_beat_lines_no_query_returns_no_match(full_set):
    result = describe_beat_lines(full_set["beat"])
    assert result["matched_line"] is None

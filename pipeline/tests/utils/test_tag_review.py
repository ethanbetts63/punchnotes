import copy

from pipeline.json_validation import validate_bit_meta
from pipeline.utils.tag_review import apply_beat_edits, build_review_beats


def _set():
    return {
        "type": "set_meta",
        "video_id": "x",
        "comedian_name": "Test",
        "start_seconds": 0,
        "bit_meta": {"1": {"beats": {"1": {
            "premise": "A thing could be an unexpected thing.",
            "joke_type": "reframe",
        }}}},
        "lines": [
            {"line_number": 1, "label": "setup", "bit": None, "beat": None, "text": "setup", "start": 0},
            {"line_number": 2, "label": "punchline", "bit": 1, "beat": 1, "text": "punch", "start": 1},
            {"line_number": 3, "label": "tag", "bit": None, "beat": None, "text": "tag a", "start": 2},
            {"line_number": 4, "label": "tag", "bit": None, "beat": None, "text": "tag b", "start": 3},
            {"line_number": 5, "label": "tag", "bit": None, "beat": None, "text": "tag c", "start": 4},
            {"line_number": 6, "label": "tag", "bit": None, "beat": None, "text": "tag d", "start": 5},
            {"line_number": 7, "label": "tag", "bit": None, "beat": None, "text": "tag e", "start": 6},
        ],
    }


def test_build_review_beats_extracts_owned_lines():
    beats = build_review_beats(_set(), min_tags=5)
    assert len(beats) == 1
    assert beats[0]["bit"] == 1 and beats[0]["beat"] == 1
    assert [line["n"] for line in beats[0]["lines"]] == [1, 2, 3, 4, 5, 6, 7]
    assert set(beats[0]["lines"][0]) == {"n", "l", "t"}


def test_build_review_beats_ignores_short_runs():
    data = _set()
    data["lines"] = data["lines"][:5]  # only 3 tags
    assert build_review_beats(data, min_tags=5) == []


def test_apply_relabel_tag_to_setup():
    data = _set()
    edit = {"bit": 1, "beat": 1, "lines": [{"n": 5, "l": "setup"}]}
    problems = apply_beat_edits(data, [edit])
    assert problems == []
    line5 = next(line for line in data["lines"] if line["line_number"] == 5)
    assert line5["label"] == "setup"
    assert line5["bit"] is None and line5["beat"] is None
    validate_bit_meta(data)


def test_apply_relabel_tag_to_fluff():
    data = _set()
    edit = {"bit": 1, "beat": 1, "lines": [{"n": 7, "l": "fluff"}]}
    assert apply_beat_edits(data, [edit]) == []
    line7 = next(line for line in data["lines"] if line["line_number"] == 7)
    assert line7["label"] == "fluff"
    validate_bit_meta(data)


def test_apply_promoting_to_punchline_is_rejected():
    data = _set()
    edit = {"bit": 1, "beat": 1, "lines": [{"n": 5, "l": "punchline"}]}
    problems = apply_beat_edits(data, [edit])
    assert problems
    line5 = next(line for line in data["lines"] if line["line_number"] == 5)
    assert line5["label"] == "tag"


def test_apply_leaves_punchline_untouched_and_rejects_changing_it():
    data = _set()
    edit = {"bit": 1, "beat": 1, "lines": [{"n": 2, "l": "setup"}]}
    problems = apply_beat_edits(data, [edit])
    assert problems
    line2 = next(line for line in data["lines"] if line["line_number"] == 2)
    assert line2["label"] == "punchline"
    assert (line2["bit"], line2["beat"]) == (1, 1)


def test_apply_does_not_mutate_input_when_dry_checking():
    data = _set()
    snapshot = copy.deepcopy(data)
    build_review_beats(data, min_tags=5)
    assert data == snapshot

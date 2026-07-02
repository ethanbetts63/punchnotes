import pytest

from pipeline.json_validation import validate_bit_meta


def _meta_with_line(line, beat_meta=None):
    return {
        "bit_meta": {"1": {"beats": {"1": beat_meta or {
            "premise": "A thing could be an unexpected thing.",
            "joke_type": "reframe",
            "subject": "a thing",
            "reframe": "an unexpected thing",
        }}}},
        "lines": [line],
    }


def _punchline(line_number=10):
    return {"line_number": line_number, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1}


def test_valid_reframe_is_accepted():
    validate_bit_meta(_meta_with_line(_punchline()))


def test_contradiction_is_valid():
    meta = _meta_with_line(_punchline())
    meta["bit_meta"]["1"]["beats"]["1"] = {
        "premise": "Financial responsibility both means avoiding debt and yet includes payday loans.",
        "joke_type": "contradiction", "subject": "financial responsibility",
        "a": "means avoiding debt", "b": "includes payday loans",
    }
    validate_bit_meta(meta)


def test_double_meaning_is_valid():
    meta = _meta_with_line(_punchline())
    meta["bit_meta"]["1"]["beats"]["1"] = {
        "premise": "'In case of fire use stairs' can mean escape or extinguish.",
        "joke_type": "double-meaning", "phrase": "in case of fire use stairs",
        "expected": "escape", "comic": "extinguish",
    }
    validate_bit_meta(meta)


def test_phonetic_match_with_reason_is_valid():
    meta = _meta_with_line(_punchline())
    meta["bit_meta"]["1"]["beats"]["1"] = {
        "premise": "'Midget' sounds like 'fidget'.", "joke_type": "phonetic-match",
        "heard": "midget", "reheard": "fidget", "reason": "ADHD",
    }
    validate_bit_meta(meta)


def test_non_fluff_line_requires_bit_and_beat():
    meta = _meta_with_line({"line_number": 10, "text": "Payoff.", "label": "punchline", "bit": None, "beat": None})
    with pytest.raises(ValueError, match="line 10: 'punchline' lines must have bit and beat values"):
        validate_bit_meta(meta)


def test_fluff_line_can_have_null_bit_and_beat():
    meta = {"bit_meta": {}, "lines": [{"line_number": 10, "text": "Thank you.", "label": "fluff", "bit": None, "beat": None}]}
    validate_bit_meta(meta)


def test_setup_line_rejects_bit_and_beat_values():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"premise": "p", "joke_type": "reframe", "subject": "x", "reframe": "y"}}}},
        "lines": [
            {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
            {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
        ],
    }
    with pytest.raises(ValueError, match="line 1: 'setup' lines must leave bit and beat null"):
        validate_bit_meta(meta)


def test_tag_before_any_punchline_is_rejected():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"premise": "p", "joke_type": "reframe", "subject": "x", "reframe": "y"}}}},
        "lines": [
            {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 2, "text": "Tag.", "label": "tag", "bit": None, "beat": None},
            {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
        ],
    }
    with pytest.raises(ValueError, match="line 2: tag must ride a preceding punchline"):
        validate_bit_meta(meta)


def test_tag_after_its_own_setup_is_valid():
    # punchline -> setup -> tag: the tag carries its own setup and stays in the beat.
    meta = {
        "bit_meta": {"1": {"beats": {"1": {
            "premise": "A thing could be an unexpected thing.",
            "joke_type": "reframe", "subject": "a thing", "reframe": "an unexpected thing",
        }}}},
        "lines": [
            {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            {"line_number": 2, "text": "New orienting line.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 3, "text": "Second payoff.", "label": "tag", "bit": None, "beat": None},
        ],
    }
    validate_bit_meta(meta)


def test_tag_after_fluff_is_rejected():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"premise": "p", "joke_type": "reframe", "subject": "x", "reframe": "y"}}}},
        "lines": [
            {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            {"line_number": 2, "text": "[laughs]", "label": "fluff", "bit": None, "beat": None},
            {"line_number": 3, "text": "Tag.", "label": "tag", "bit": None, "beat": None},
        ],
    }
    with pytest.raises(ValueError, match="line 3: tag must follow a punchline, tag, or its own setup"):
        validate_bit_meta(meta)


def test_multi_beat_bit_is_valid():
    meta = {
        "bit_meta": {"1": {"beats": {
            "1": {"premise": "p1", "joke_type": "reframe", "subject": "x", "reframe": "y"},
            "2": {"premise": "p2", "joke_type": "reframe", "subject": "a", "reframe": "b"},
        }}},
        "lines": [
            {"line_number": 1, "text": "A", "label": "punchline", "bit": 1, "beat": 1},
            {"line_number": 2, "text": "B", "label": "punchline", "bit": 1, "beat": 2},
        ],
    }
    validate_bit_meta(meta)


def test_consecutive_split_punchline_lines_in_same_beat_are_valid():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {
            "premise": "A thing could be an unexpected thing.",
            "joke_type": "reframe",
            "subject": "a thing",
            "reframe": "an unexpected thing",
        }}}},
        "lines": [
            {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 2, "text": "Split payoff part one.", "label": "punchline", "bit": 1, "beat": 1},
            {"line_number": 3, "text": "Split payoff part two.", "label": "punchline", "bit": 1, "beat": 1},
        ],
    }
    validate_bit_meta(meta)


def test_repeated_punchline_anchor_after_setup_is_rejected():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {
            "premise": "'Pussy' can mean a cat or a sexual reference.",
            "joke_type": "double-meaning",
            "phrase": "pussy",
            "expected": "a cat",
            "comic": "a sexual reference",
        }}}},
        "lines": [
            {"line_number": 1371, "text": "I'm a cat guy.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 1378, "text": "When I say I love pussy, that's what I'm talking about.", "label": "punchline", "bit": 1, "beat": 1},
            {"line_number": 1380, "text": 'People are like, "I want to crush it."', "label": "setup", "bit": None, "beat": None},
            {"line_number": 1381, "text": 'I\'m like, "Really? I want to snuggle it."', "label": "punchline", "bit": 1, "beat": 1},
        ],
    }
    with pytest.raises(ValueError, match="bit 1 beat 1: multiple punchline lines"):
        validate_bit_meta(meta)


def test_bit_level_premise_is_rejected():
    meta = _meta_with_line(_punchline())
    meta["bit_meta"]["1"]["premise"] = "Old bit-level field."
    with pytest.raises(ValueError, match="bit 1: premise belongs on each beat, not on the bit"):
        validate_bit_meta(meta)


def test_bit_meta_must_be_object_not_array():
    meta = {"bit_meta": [], "lines": [{"line_number": 1, "text": "P.", "label": "punchline", "bit": 1, "beat": 1}]}
    with pytest.raises(ValueError, match="bit_meta must be a JSON object"):
        validate_bit_meta(meta)


def test_beats_must_be_object_not_array():
    meta = {"bit_meta": {"1": {"beats": []}}, "lines": [{"line_number": 1, "text": "P.", "label": "punchline", "bit": 1, "beat": 1}]}
    with pytest.raises(ValueError, match="bit 1: beats must be a JSON object"):
        validate_bit_meta(meta)


def test_punchline_referencing_missing_beat_is_rejected():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"premise": "p", "joke_type": "reframe", "subject": "x", "reframe": "y"}}}},
        "lines": [{"line_number": 1, "text": "P.", "label": "punchline", "bit": 2, "beat": 1}],
    }
    with pytest.raises(ValueError, match=r"line\(s\) 1: punchline references bit 2 beat 1"):
        validate_bit_meta(meta)


def test_single_line_punchline_uses_line_text_as_premise():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"joke_type": "reframe", "subject": "seatbelts", "reframe": "wanting a hug"}}}},
        "lines": [{"line_number": 10, "text": "I just wanna be held, please.", "label": "punchline", "bit": 1, "beat": 1}],
    }
    validate_bit_meta(meta)
    assert meta["bit_meta"]["1"]["beats"]["1"]["premise"] == "I just wanna be held, please."


def test_setup_backed_beat_requires_written_premise():
    meta = {
        "bit_meta": {"1": {"beats": {"1": {"joke_type": "reframe", "subject": "seatbelts", "reframe": "wanting a hug"}}}},
        "lines": [
            {"line_number": 9, "text": "I started wearing my seatbelt.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 10, "text": "I just wanna be held, please.", "label": "punchline", "bit": 1, "beat": 1},
        ],
    }
    with pytest.raises(ValueError, match="bit 1 beat 1: premise is required"):
        validate_bit_meta(meta)

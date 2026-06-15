from pipeline.utils.ownership import infer_line_ownership


def _lines(*entries):
    return [{"line_number": i + 1, "text": "-", "label": label, "bit": bit, "beat": beat}
            for i, (label, bit, beat) in enumerate(entries)]


def test_setup_gets_next_punchline_bit_and_beat():
    lines = _lines(("setup", None, None), ("punchline", 1, 1))
    assert infer_line_ownership(lines)[1] == (1, 1)


def test_tag_gets_previous_punchline_bit_and_beat():
    lines = _lines(("punchline", 1, 1), ("tag", None, None))
    assert infer_line_ownership(lines)[2] == (1, 1)


def test_fluff_inside_beat_inferred_from_punchline_anchor():
    lines = _lines(("setup", None, None), ("fluff", None, None), ("punchline", 1, 1))
    assert infer_line_ownership(lines)[2] == (1, 1)


def test_fluff_between_beats_gets_bit_and_null_beat():
    lines = _lines(("punchline", 1, 1), ("fluff", None, None), ("punchline", 1, 2))
    assert infer_line_ownership(lines)[2] == (1, None)


def test_fluff_inside_beat_gets_bit_and_beat():
    lines = _lines(("setup", 1, 1), ("fluff", None, None), ("punchline", 1, 1))
    assert infer_line_ownership(lines)[2] == (1, 1)


def test_fluff_outside_bit_stays_null():
    lines = _lines(("fluff", 9, 9), ("setup", 1, 1), ("punchline", 1, 1), ("fluff", 9, 9))
    ownership = infer_line_ownership(lines)
    assert ownership[1] == (None, None)
    assert ownership[4] == (None, None)


def test_inference_does_not_mutate_original_lines():
    lines = _lines(("setup", 1, 1), ("fluff", None, None), ("punchline", 1, 1))
    infer_line_ownership(lines)
    assert lines[1]["bit"] is None
    assert lines[1]["beat"] is None

from pipeline.management.commands.find_long_tag_runs import find_long_tag_runs


def _lines(*entries):
    out = []
    for i, entry in enumerate(entries):
        label, bit, beat = entry
        out.append({"line_number": i + 1, "label": label, "bit": bit, "beat": beat, "text": "-"})
    return out


def test_flags_run_of_min_tags():
    lines = _lines(
        ("punchline", 1, 1),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
    )
    runs = find_long_tag_runs(lines, min_tags=4)
    assert runs == [{"bit": 1, "beat": 1, "tag_count": 4, "line_start": 2, "line_end": 5}]


def test_ignores_short_run():
    lines = _lines(
        ("punchline", 1, 1),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
    )
    assert find_long_tag_runs(lines, min_tags=4) == []


def test_run_is_anchored_to_most_recent_punchline():
    lines = _lines(
        ("punchline", 2, 3),
        ("setup", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
    )
    runs = find_long_tag_runs(lines, min_tags=4)
    assert runs[0]["bit"] == 2
    assert runs[0]["beat"] == 3


def test_intervening_non_tag_breaks_the_run():
    lines = _lines(
        ("punchline", 1, 1),
        ("tag", None, None),
        ("tag", None, None),
        ("fluff", None, None),
        ("tag", None, None),
        ("tag", None, None),
    )
    assert find_long_tag_runs(lines, min_tags=4) == []


def test_multiple_runs_in_one_set():
    lines = _lines(
        ("punchline", 1, 1),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("setup", None, None),
        ("punchline", 1, 2),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
        ("tag", None, None),
    )
    runs = find_long_tag_runs(lines, min_tags=4)
    assert len(runs) == 2
    assert runs[0]["beat"] == 1
    assert runs[1]["beat"] == 2

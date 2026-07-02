import json

from django.core.management import call_command

from pipeline.json_validation import validate_bit_meta


def _write_set(path):
    data = {
        "type": "set_meta",
        "video_id": "x",
        "comedian_name": "Test",
        "start_seconds": 0,
        "interview_end_line": None,
        "interview_end_seconds": None,
        "set_attributes": [],
        "comedian_attributes": [],
        "bit_meta": {"1": {"beats": {"1": {
            "premise": "A thing could be an unexpected thing.",
            "joke_type": "reframe",
        }}}},
        "lines": [
            {"text": "setup", "label": "setup", "bit": None, "beat": None, "line_number": 1, "start": 0},
            {"text": "punch", "label": "punchline", "bit": 1, "beat": 1, "line_number": 2, "start": 1},
            {"text": "tag a", "label": "tag", "bit": None, "beat": None, "line_number": 3, "start": 2},
            {"text": "tag b", "label": "tag", "bit": None, "beat": None, "line_number": 4, "start": 3},
            {"text": "tag c", "label": "tag", "bit": None, "beat": None, "line_number": 5, "start": 4},
            {"text": "tag d", "label": "tag", "bit": None, "beat": None, "line_number": 6, "start": 5},
            {"text": "tag e", "label": "tag", "bit": None, "beat": None, "line_number": 7, "start": 6},
        ],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def test_extract_then_apply_relabel_round_trip(tmp_path):
    archive = tmp_path / "archive"
    archive.mkdir()
    review = tmp_path / "review"
    set_path = archive / "set_one.json"
    _write_set(set_path)

    call_command("extract_tag_runs", path=archive, out_dir=review, min_tags=5)

    batches = sorted(review.glob("batch_*.json"))
    assert len(batches) == 1
    batch = json.loads(batches[0].read_text(encoding="utf-8"))
    assert len(batch["beats"]) == 1

    # Simulate the reviewer: relabel the second-to-last tag as a setup.
    for line in batch["beats"][0]["lines"]:
        if line["n"] == 6:
            line["l"] = "setup"
    batches[0].write_text(json.dumps(batch), encoding="utf-8")

    call_command("apply_tag_run_review", review_dir=review, archive=archive)

    updated = json.loads(set_path.read_text(encoding="utf-8-sig"))
    line6 = next(line for line in updated["lines"] if line["line_number"] == 6)
    assert line6["label"] == "setup"
    validate_bit_meta(updated)

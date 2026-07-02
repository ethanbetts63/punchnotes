"""Helpers for the tag-run re-evaluation workflow.

`build_review_beats` pulls each flagged beat's own lines out of an annotated
set so a reviewer never needs the surrounding transcript. `apply_beat_edits`
takes the reviewer's corrected labels back and rewrites the set in place,
supporting two operations: relabelling a line, and splitting one beat into two
by promoting a line to a new `punchline`.
"""

from pipeline.management.commands.find_long_tag_runs import find_long_tag_runs
from pipeline.utils.ownership import infer_line_ownership

RELABEL_TARGETS = {"setup", "tag", "fluff"}


def gather_beat_lines(lines_data: list, bit: int, beat: int) -> list[dict]:
    """Return the lines owned by (bit, beat) in transcript order."""
    ownership = infer_line_ownership(lines_data)
    return [
        line
        for line in lines_data
        if ownership.get(int(line["line_number"])) == (bit, beat)
    ]


def build_review_beats(data: dict, min_tags: int) -> list[dict]:
    """Return one review object per flagged beat in a single annotated set."""
    lines_data = data.get("lines", [])
    runs = find_long_tag_runs(lines_data, min_tags)

    seen: set[tuple[int, int]] = set()
    beats: list[dict] = []
    for run in runs:
        key = (run["bit"], run["beat"])
        if key in seen or run["bit"] is None or run["beat"] is None:
            continue
        seen.add(key)
        beats.append({
            "bit": run["bit"],
            "beat": run["beat"],
            "lines": [
                {"n": line["line_number"], "l": line["label"], "t": line.get("text", "")}
                for line in gather_beat_lines(lines_data, run["bit"], run["beat"])
            ],
        })
    return beats


def apply_beat_edits(data: dict, edits: list[dict]) -> list[str]:
    """Apply reviewer relabels for one set file. Returns a list of problems.

    Each edit is a review object whose `lines` carry the reviewer's final label
    in `l`. Only `setup`/`tag`/`fluff` relabels are allowed; punchline lines are
    left untouched and no new beats are created. Mutates `data` in place; the
    caller validates after.
    """
    problems: list[str] = []
    lines_by_number = {int(line["line_number"]): line for line in data["lines"]}

    for edit in edits:
        for entry in edit["lines"]:
            line_number = int(entry["n"])
            target = lines_by_number.get(line_number)
            if target is None:
                problems.append(f"bit {edit['bit']} beat {edit['beat']}: line {line_number} not found in set")
                continue

            new_label = entry.get("l")

            if target.get("label") == "punchline":
                if new_label != "punchline":
                    problems.append(f"line {line_number}: a punchline line may not be relabelled in this pass")
                continue

            if new_label not in RELABEL_TARGETS:
                problems.append(
                    f"line {line_number}: label must be one of setup, tag, fluff; got {new_label!r}"
                )
                continue

            target["label"] = new_label
            target["bit"] = None
            target["beat"] = None

    return problems

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def find_long_tag_runs(lines: list, min_tags: int) -> list[dict]:
    """Return each maximal run of >= min_tags consecutive `tag` lines.

    A tag belongs to the most recent punchline's beat, so a pure run of tags
    all sits in one beat — the beat anchored by the punchline before the run.
    """
    runs: list[dict] = []
    current_bit = None
    current_beat = None
    run_lines: list = []

    def flush():
        if len(run_lines) >= min_tags:
            runs.append({
                "bit": current_bit,
                "beat": current_beat,
                "tag_count": len(run_lines),
                "line_start": run_lines[0],
                "line_end": run_lines[-1],
            })

    for line in lines:
        if not isinstance(line, dict):
            continue
        label = line.get("label")
        line_number = line.get("line_number")

        if label == "tag":
            run_lines.append(line_number)
            continue

        flush()
        run_lines = []

        if label == "punchline" and line.get("bit") is not None and line.get("beat") is not None:
            current_bit = line.get("bit")
            current_beat = line.get("beat")

    flush()
    return runs


class Command(BaseCommand):
    help = "List archived beats with a run of consecutive tags (candidates for re-annotation)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=Path,
            default=settings.PIPELINE_PRIVATE_DATA_DIR / "bit_annotated_set_archive",
            help="Directory of annotated set JSON files to scan.",
        )
        parser.add_argument(
            "--min-tags",
            type=int,
            default=4,
            help="Minimum consecutive tags to flag (default: 4).",
        )
        parser.add_argument(
            "--output",
            type=Path,
            default=settings.PIPELINE_PRIVATE_DATA_DIR / "long_tag_runs.tsv",
            help="File to write the report to.",
        )

    def handle(self, *args, **options):
        archive: Path = options["path"]
        min_tags: int = options["min_tags"]
        output: Path = options["output"]

        paths = sorted(archive.glob("*.json"))
        if not paths:
            self.stdout.write(f"No JSON files found in {archive}.")
            return

        rows: list[str] = []
        files_with_issues = 0
        for path in paths:
            try:
                data = json.loads(path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, OSError) as exc:
                self.stderr.write(f"Skipping {path.name}: {exc}")
                continue

            runs = find_long_tag_runs(data.get("lines", []), min_tags)
            if runs:
                files_with_issues += 1
            for run in runs:
                rows.append(
                    f"{path}\tbit={run['bit']}\tbeat={run['beat']}"
                    f"\ttags={run['tag_count']}\tlines={run['line_start']}-{run['line_end']}"
                )

        header = f"# file\tbit\tbeat\ttag_count\tline_range  (runs of >= {min_tags} consecutive tags)\n"
        output.write_text(header + "\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")

        self.stdout.write(
            self.style.SUCCESS(
                f"Scanned {len(paths)} files; found {len(rows)} tag run(s) "
                f"across {files_with_issues} file(s). Wrote {output}."
            )
        )

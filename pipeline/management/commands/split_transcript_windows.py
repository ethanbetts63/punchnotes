import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pipeline.import_utils.transcript_windows import write_inbox_transcript_windows


def is_window_file(path: Path) -> bool:
    return "_window" in path.stem


class Command(BaseCommand):
    help = "Split full transcript JSON files into music-cue windows for 1_transcript_inbox."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="+",
            help="Transcript JSON file(s), or directories containing transcript JSON files.",
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            default=settings.PIPELINE_DATA_DIR / "1_transcript_inbox",
            help="Directory to write window files into. Defaults to pipeline/data/1_transcript_inbox.",
        )
        parser.add_argument(
            "--overlap",
            type=int,
            default=25,
            help="Number of lines before each music cue to include. Default: 25.",
        )
        parser.add_argument(
            "--min-lines",
            type=int,
            default=20,
            help="Skip generated windows shorter than this many lines. Default: 20.",
        )

    def handle(self, *args, **options):
        sources = self._expand_sources(options["paths"])
        if not sources:
            self.stdout.write("No full transcript JSON files found.")
            return

        output_dir = options["output_dir"]
        overlap = options["overlap"]
        min_lines = options["min_lines"]

        total_written = 0
        for source in sources:
            doc = json.loads(source.read_text(encoding="utf-8-sig"))
            video_id = doc.get("video_id") or source.stem
            paths = write_inbox_transcript_windows(
                doc,
                output_dir,
                overlap=overlap,
                min_lines=min_lines,
                overwrite=True,
            )
            total_written += len(paths)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{video_id}: wrote {len(paths)} file(s) from {source.name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Split {len(sources)} transcript(s); wrote {total_written} file(s)."
            )
        )

    def _expand_sources(self, raw_paths):
        sources = []
        for raw_path in raw_paths:
            path = Path(raw_path)
            if not path.is_absolute():
                path = Path.cwd() / path

            if path.is_dir():
                sources.extend(
                    candidate
                    for candidate in sorted(path.glob("*.json"))
                    if not is_window_file(candidate)
                )
            elif path.is_file():
                if is_window_file(path):
                    self.stdout.write(f"Skipping existing window file: {path.name}")
                else:
                    sources.append(path)
            else:
                raise CommandError(f"Path does not exist: {path}")

        unique_sources = []
        seen = set()
        for source in sources:
            resolved = source.resolve()
            if resolved not in seen:
                unique_sources.append(source)
                seen.add(resolved)

        return unique_sources

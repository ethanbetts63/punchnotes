import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.utils.formatters import serialize_annotated_set, serialize_transcript


def normalize_path(path, serializer):
    raw = path.read_text(encoding="utf-8-sig")
    data = json.loads(raw)
    new = serializer(data)
    if new == raw.replace("\r\n", "\n"):
        return False

    with open(path, "w", encoding="utf-8", newline="\n") as file:
        file.write(new)
    return True


class Command(BaseCommand):
    help = "Normalize JSON formatting of archived annotated sets and transcripts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sets-path",
            type=Path,
            help="Directory of annotated set JSON files to normalize.",
        )
        parser.add_argument(
            "--transcripts-path",
            type=Path,
            help="Directory of transcript JSON files to normalize.",
        )

    def handle(self, *args, **options):
        sets_path = options.get("sets_path")
        transcripts_path = options.get("transcripts_path")
        if sets_path or transcripts_path:
            archives = []
            if sets_path:
                archives.append(("bit annotated sets", sets_path, serialize_annotated_set))
            if transcripts_path:
                archives.append(("transcripts", transcripts_path, serialize_transcript))
        else:
            archives = [
                (
                    "bit annotated sets",
                    settings.PIPELINE_DATA_DIR / "bit_annotated_set_archive",
                    serialize_annotated_set,
                ),
                (
                    "transcripts",
                    settings.PIPELINE_DATA_DIR / "transcript_archive",
                    serialize_transcript,
                ),
            ]

        total_changed = 0
        total_paths = 0
        for label, archive, serializer in archives:
            paths = sorted(archive.glob("*.json"))
            changed = sum(1 for path in paths if normalize_path(path, serializer))
            total_changed += changed
            total_paths += len(paths)
            self.stdout.write(f"Normalized {changed}/{len(paths)} {label}.")

        if not total_paths:
            self.stdout.write("No files found.")
            return

        self.stdout.write(self.style.SUCCESS(f"Normalized {total_changed}/{total_paths} files."))

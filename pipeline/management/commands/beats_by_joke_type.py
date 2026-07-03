from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.utils.beats_by_joke_type import (
    build_report,
    normalize_joke_book,
    normalize_joke_type,
    render_json,
    render_txt,
    resolve_comedian,
)


class Command(BaseCommand):
    help = (
        "List every beat of a given joke type, optionally scoped to a comedian and/or a "
        "joke-book size their set earned. Writes the beat's transcript lines plus a "
        "copy-pasteable set slug (video-setNN-comedian?bit=NNN&beat=NNN) per beat."
    )

    def add_arguments(self, parser):
        parser.add_argument("--comedian", help="Comedian name or slug (omit to include every comedian)")
        parser.add_argument(
            "--joke-type",
            required=True,
            help="Joke type, e.g. analogy, misdirect, double-meaning, reframe, phonetic-match, "
            "contradiction, hyperbole, elephant-in-the-room, anti-humor",
        )
        parser.add_argument(
            "--joke-book",
            choices=["small", "medium", "large"],
            help="Only include beats from sets that earned this joke book size",
        )
        parser.add_argument("--format", choices=["txt", "json"], default="txt")
        parser.add_argument(
            "--output",
            help="Output file path (default: pipeline/data_private/beat_reports/<parts>.<ext>)",
        )

    def handle(self, *args, **options):
        comedian = resolve_comedian(options["comedian"]) if options["comedian"] else None
        joke_type = normalize_joke_type(options["joke_type"])
        joke_book = normalize_joke_book(options["joke_book"]) if options["joke_book"] else None
        report = build_report(joke_type, comedian=comedian, joke_book=joke_book)

        fmt = options["format"]
        if options["output"]:
            output_path = Path(options["output"])
        else:
            out_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "beat_reports"
            name_parts = [joke_type]
            if comedian:
                name_parts.append(comedian.slug)
            if joke_book:
                name_parts.append(f"{joke_book}-joke-book")
            output_path = out_dir / f"{'_'.join(name_parts)}.{fmt}"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = (
            render_txt(report)
            if fmt == "txt"
            else render_json(joke_type, report, comedian=comedian, joke_book=joke_book)
        )
        output_path.write_text(content, encoding="utf-8")

        who = comedian.name if comedian else "all comedians"
        book = f", {joke_book} joke book" if joke_book else ""
        self.stdout.write(
            self.style.SUCCESS(f"{len(report)} beat(s) for {who} ({joke_type}{book}) written to {output_path}")
        )

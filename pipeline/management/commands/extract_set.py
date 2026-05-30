import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from pipeline.models.comedian import ATTRIBUTE_VALUES


AUDIENCE_REACTION_RE = re.compile(
    r"^\s*[\[(]?\s*(audience\s+)?"
    r"(laughing|laughs|laughter|cheering|cheers|applause|applauding)"
    r"[\])]?\s*$",
    re.IGNORECASE,
)

JOKE_BOOK_VALUES = {"small", "medium", "large"}
def dump_set(doc):
    """Pretty-print set metadata with one compact JSON object per line."""
    non_lines = [(k, v) for k, v in doc.items() if k != "lines"]
    parts = ["{"]
    for i, (key, value) in enumerate(non_lines):
        parts.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)},")

    parts.append('  "lines": [')
    for i, line in enumerate(doc["lines"]):
        comma = "," if i < len(doc["lines"]) - 1 else ""
        parts.append(f"    {json.dumps(line, ensure_ascii=False)}{comma}")
    parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


def parse_guests(episode_title):
    if " - " not in episode_title:
        return []

    guest_text = episode_title.split(" - ", 1)[1]
    guest_text = re.sub(r"^KT\s*#?\d+\s*", "", guest_text, flags=re.IGNORECASE).strip()
    names = re.split(r"\s*(?:\+|&|,)\s*", guest_text)
    return [name.title() for name in names if name.strip()]


def slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


def parse_line_numbers(value):
    if not value:
        return set()

    line_numbers = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        line_numbers.add(int(part))
    return line_numbers


def normalize_joke_book(value):
    if value is None:
        return None

    text = value.strip().lower()
    if not text or text in {"null", "none", "unknown", "unclear"}:
        return None
    if text in JOKE_BOOK_VALUES:
        return text
    raise CommandError("--joke-book must be one of small, medium, large, or null")


def normalize_attributes(value):
    if not value:
        return []

    attributes = []
    seen = set()
    parts = value.split(",")

    for raw_part in parts:
        part = raw_part.strip().lower().replace(" ", "_")
        if part == "middle_age":
            part = "middle-age"
        if not part:
            continue

        if part not in ATTRIBUTE_VALUES:
            allowed = ", ".join(sorted(ATTRIBUTE_VALUES))
            raise CommandError(
                "--comedian-attributes must be a comma-separated list using "
                f"{allowed}"
            )

        if part not in seen:
            attributes.append(part)
            seen.add(part)

    return attributes


def find_source_line(source_lines, target_line_number):
    for i, line in enumerate(source_lines, start=1):
        if line.get("line_number", i) == target_line_number:
            return line
    raise CommandError(f"--interview-end-line not found in transcript: {target_line_number}")


def line_end_seconds(line):
    start = line.get("start")
    if start is None:
        return None

    duration = line.get("duration")
    if duration is None:
        return start

    return start + duration


class Command(BaseCommand):
    help = "Extract one stand-up set from a transcript line range into pipeline/data/2_set_inbox/"

    def add_arguments(self, parser):
        parser.add_argument("--transcript", required=True, help="Path to transcript JSON")
        parser.add_argument("--start-line", required=True, type=int, help="First source line number to include")
        parser.add_argument("--end-line", required=True, type=int, help="Last source line number to include")
        parser.add_argument("--comedian-name", required=True, help="Comedian name for metadata and filename")
        parser.add_argument(
            "--set-number",
            required=False,
            type=int,
            help="Deprecated; import derives set order from start_seconds.",
        )
        parser.add_argument(
            "--omit-lines",
            default="",
            help="Comma-separated source line numbers to omit from the extracted set",
        )
        parser.add_argument(
            "--joke-book",
            default=None,
            help="Joke book size awarded after the interview: small, medium, large, or null",
        )
        parser.add_argument(
            "--interview-end-line",
            type=int,
            default=None,
            help="Last source line number belonging to this comic's post-set interview",
        )
        parser.add_argument(
            "--comedian-attributes",
            dest="attributes",
            default="",
            help=(
                "Comma-separated explicit comic attributes from the transcript, e.g. "
                "bucket_pull,gay,black"
            ),
        )

    def handle(self, *args, **options):
        transcript_path = Path(options["transcript"])
        if not transcript_path.is_absolute():
            transcript_path = settings.BASE_DIR / transcript_path
        if not transcript_path.exists():
            raise CommandError(f"Transcript not found: {transcript_path}")

        start_line = options["start_line"]
        end_line = options["end_line"]
        if start_line > end_line:
            raise CommandError("--start-line must be less than or equal to --end-line")

        omitted_line_numbers = parse_line_numbers(options["omit_lines"])
        transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
        source_lines = transcript.get("lines")
        if not isinstance(source_lines, list):
            raise CommandError("Transcript JSON must contain a top-level lines array")

        selected_lines = []
        for i, line in enumerate(source_lines, start=1):
            line_number = line.get("line_number", i)
            if line_number < start_line or line_number > end_line:
                continue
            if line_number in omitted_line_numbers:
                continue
            text = line.get("text", "")
            if AUDIENCE_REACTION_RE.match(text):
                continue

            selected_lines.append(
                {
                    "line_number": line_number,
                    "text": text,
                    "start": line["start"],
                    "label": "",
                }
            )

        if not selected_lines:
            raise CommandError("No lines selected for this range")

        interview_end_line = options["interview_end_line"]
        interview_end_seconds = None
        if interview_end_line is not None:
            if interview_end_line < end_line:
                raise CommandError("--interview-end-line must be greater than or equal to --end-line")
            interview_end_seconds = line_end_seconds(find_source_line(source_lines, interview_end_line))

        video_id = transcript["video_id"]
        comedian_name = options["comedian_name"]
        output_name = f"{video_id}_line{start_line:05d}_{slugify(comedian_name)}.json"
        output_dir = settings.PIPELINE_DATA_DIR / "2_set_inbox"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_name

        set_doc = {
            "type": "set_meta",
            "video_id": video_id,
            "episode_title": transcript["episode_title"],
            "episode_url": transcript["episode_url"],
            "publish_date": transcript.get("publish_date"),
            "guests": parse_guests(transcript["episode_title"]),
            "comedian_name": comedian_name,
            "start_seconds": selected_lines[0]["start"],
            "interview_end_line": interview_end_line,
            "interview_end_seconds": interview_end_seconds,
            "joke_book": normalize_joke_book(options["joke_book"]),
            "attributes": normalize_attributes(options["attributes"]),
            "lines": selected_lines,
        }

        output_path.write_text(dump_set(set_doc), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {output_path} with {len(selected_lines)} lines "
                f"from source lines {start_line}-{end_line}"
            )
        )

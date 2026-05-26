import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


AUDIENCE_REACTION_RE = re.compile(
    r"^\s*[\[(]?\s*(audience\s+)?"
    r"(laughing|laughs|laughter|cheering|cheers|applause|applauding)"
    r"[\])]?\s*$",
    re.IGNORECASE,
)


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


class Command(BaseCommand):
    help = "Extract one stand-up set from a transcript line range into data/set_inbox/"

    def add_arguments(self, parser):
        parser.add_argument("--transcript", required=True, help="Path to transcript JSON")
        parser.add_argument("--start-line", required=True, type=int, help="First source line number to include")
        parser.add_argument("--end-line", required=True, type=int, help="Last source line number to include")
        parser.add_argument("--comedian-name", required=True, help="Comedian name for metadata and filename")
        parser.add_argument(
            "--comedian-type",
            required=True,
            choices=["bucket_pull", "regular", "golden_ticket"],
            help="Type of Kill Tony appearance",
        )
        parser.add_argument("--set-number", required=True, type=int, help="1-indexed set number in show order")
        parser.add_argument(
            "--omit-lines",
            default="",
            help="Comma-separated source line numbers to omit from the extracted set",
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

        video_id = transcript["video_id"]
        set_number = options["set_number"]
        comedian_name = options["comedian_name"]
        output_name = f"{video_id}_set{set_number:02d}_{slugify(comedian_name)}.json"
        output_dir = settings.BASE_DIR / "data" / "2_set_inbox"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_name

        set_doc = {
            "type": "set_meta",
            "video_id": video_id,
            "episode_title": transcript["episode_title"],
            "episode_url": transcript["episode_url"],
            "publish_date": transcript.get("publish_date"),
            "guests": parse_guests(transcript["episode_title"]),
            "comedian_name": comedian_name,
            "comedian_type": options["comedian_type"],
            "set_number": set_number,
            "start_seconds": selected_lines[0]["start"],
            "lines": selected_lines,
        }

        output_path.write_text(dump_set(set_doc), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Wrote {output_path} with {len(selected_lines)} lines "
                f"from source lines {start_line}-{end_line}"
            )
        )

# scrape_podscripts.py
#
# Scrapes Kill Tony transcripts from podscripts.co as a free, fast alternative to
# the Whisper pipeline (no audio download, no GPU time).
#
# KNOWN LIMITATION — line granularity
# ------------------------------------
# Podscripts segments transcripts by timestamp group, producing roughly one line
# per 30–60 seconds of audio. Whisper, by contrast, splits on acoustic pauses,
# yielding one line per ~3–5 seconds and often one line per comedic beat.
#
# This matters for the labelling step (setup / punchline / tag / fluff): those
# labels work best when each line is a single utterance separated by a natural
# pause. Splitting podscripts lines on sentence boundaries (". ", "? ", "! ")
# would recover some granularity, but it throws away exactly the information
# that makes pause-based splitting valuable — a pause mid-sentence signals a
# beat boundary that punctuation cannot capture.
#
# Practical consequence: transcripts scraped here can be used to locate sets
# (extract_set.py) but the resulting set files are harder to label accurately.
# The Whisper pipeline remains the better source for any episode where per-beat
# analysis is needed.
#
# One possible future path: run a forced-alignment tool (e.g. whisperX, aeneas)
# against the raw audio using the podscripts text as a reference, recovering
# pause-level timing without a full re-transcription. Left for another day.

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.utils.transcript_windows import write_inbox_transcript_windows
from pipeline.models import Video

BASE_URL = "https://podscripts.co"
PODCAST_PATH = "/podcasts/kill-tony"

TIMESTAMP_RE = re.compile(r"Starting point is (\d{1,2}):(\d{2}):(\d{2})")
EPISODE_NUM_RE = re.compile(r"#(\d+)")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def hms_to_seconds(h: str, m: str, s: str) -> int:
    return int(h) * 3600 + int(m) * 60 + int(s)


def dump_episode(doc: dict) -> str:
    """Same compact format as generate_transcripts.py so downstream tools work unchanged."""
    non_line = [(k, v) for k, v in doc.items() if k != "lines"]
    has_lines = "lines" in doc
    parts = ["{"]
    for i, (k, v) in enumerate(non_line):
        comma = "," if i < len(non_line) - 1 or has_lines else ""
        parts.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    if has_lines:
        parts.append('  "lines": [')
        doc_lines = doc["lines"]
        for i, line in enumerate(doc_lines):
            comma = "," if i < len(doc_lines) - 1 else ""
            parts.append(f"    {json.dumps(line, ensure_ascii=False)}{comma}")
        parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


class Command(BaseCommand):
    help = "Scrape Kill Tony transcripts from podscripts.co into pipeline/data/1_transcript_inbox/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--episode",
            type=int,
            default=None,
            metavar="N",
            help="Scrape a single episode by number",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Scrape all episodes that have an Episode record in the DB",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Re-scrape episodes that already have a transcript file",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.5,
            metavar="SECS",
            help="Pause between HTTP requests (default: 1.5)",
        )
        parser.add_argument(
            "--refresh-index",
            action="store_true",
            help="Rebuild the episode→URL index even if it already exists",
        )

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR
        inbox_path = data_dir / "1_transcript_inbox"
        archive_path = data_dir / "transcript_archive"
        inbox_path.mkdir(parents=True, exist_ok=True)
        archive_path.mkdir(parents=True, exist_ok=True)
        index_path = data_dir / "podscripts_index.json"
        delay = options["delay"]

        session = requests.Session()
        session.headers.update(HEADERS)

        # --- Build or load episode index ---
        if not index_path.exists() or options["refresh_index"]:
            self.stdout.write("Building episode index from podscripts.co listing pages...")
            index = self._build_index(session, delay)
            index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
            self.stdout.write(f"Indexed {len(index)} episodes → saved to {index_path.name}")
        else:
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.stdout.write(f"Loaded index: {len(index)} episodes (use --refresh-index to update)")

        # --- Determine target episode numbers ---
        if options["episode"]:
            targets = [options["episode"]]
        elif options["all"]:
            targets = list(
                Video.objects.exclude(video_id__isnull=True)
                .exclude(number__isnull=True)
                .values_list("number", flat=True)
            )
        else:
            self.stderr.write(self.style.ERROR("Specify --episode N or --all"))
            return

        if not targets:
            self.stdout.write("No target episodes found.")
            return

        self.stdout.write(f"Targeting {len(targets)} episode(s)...\n")

        # --- Scrape each target ---
        ok = skipped = failed = 0
        for ep_num in sorted(targets):
            ep_key = str(ep_num)
            if ep_key not in index:
                self.stdout.write(self.style.WARNING(f"  #{ep_num}: not in podscripts index"))
                failed += 1
                continue

            try:
                ep_obj = Video.objects.get(number=ep_num)
            except Video.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  #{ep_num}: no Video record in DB"))
                failed += 1
                continue

            archive_file = archive_path / f"{ep_obj.video_id}.json"
            existing_inbox_files = list(inbox_path.glob(f"{ep_obj.video_id}*.json"))
            if (archive_file.exists() or existing_inbox_files) and not options["overwrite"]:
                self.stdout.write(f"  #{ep_num}: already exists, skipping (--overwrite to redo)")
                skipped += 1
                continue

            self.stdout.write(f"  #{ep_num}: fetching transcript...")
            try:
                lines = self._scrape_transcript(session, index[ep_key])
                time.sleep(delay)
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  #{ep_num}: failed — {exc}"))
                failed += 1
                continue

            doc = {
                "type": "episode_meta",
                "video_id": ep_obj.video_id,
                "episode_title": ep_obj.title,
                "episode_url": ep_obj.url,
                "publish_date": ep_obj.date.isoformat() if ep_obj.date else None,
                "lines": lines,
            }
            archive_file.write_text(dump_episode(doc), encoding="utf-8")
            inbox_files = write_inbox_transcript_windows(doc, inbox_path, overlap=25)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  #{ep_num}: {len(lines)} lines archived; "
                    f"{len(inbox_files)} inbox transcript window(s)"
                )
            )
            ok += 1

        self.stdout.write(f"\nDone: {ok} scraped, {skipped} skipped, {failed} failed.")

    def _build_index(self, session: requests.Session, delay: float) -> dict:
        """Crawl all listing pages and return {episode_number_str: relative_path}."""
        index: dict[str, str] = {}
        page = 1
        while True:
            url = f"{BASE_URL}{PODCAST_PATH}?page={page}"
            self.stdout.write(f"  page {page}...")
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            links = soup.select("h3 a[href]")
            if not links:
                break

            found_on_page = 0
            for a in links:
                href = a.get("href", "")
                title = a.get_text()
                m = EPISODE_NUM_RE.search(title)
                if m and href.startswith(PODCAST_PATH):
                    index[m.group(1)] = href
                    found_on_page += 1

            if found_on_page == 0:
                break

            page += 1
            time.sleep(delay)

        return index

    def _scrape_transcript(self, session: requests.Session, path: str) -> list[dict]:
        """Parse one transcript page into a list of line dicts."""
        url = f"{BASE_URL}{path}"
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        lines = []
        line_number = 1
        for group in soup.select("div.single-sentence"):
            ts_span = group.select_one("span.pod_timestamp_indicator")
            if not ts_span:
                continue
            m = TIMESTAMP_RE.search(ts_span.get_text())
            if not m:
                continue
            start = hms_to_seconds(m.group(1), m.group(2), m.group(3))

            texts = [
                span.get_text(" ", strip=True)
                for span in group.select("span.transcript-text")
                if span.get_text(strip=True)
            ]
            if not texts:
                continue

            lines.append(
                {
                    "line_number": line_number,
                    "text": " ".join(texts),
                    "start": start,
                }
            )
            line_number += 1

        return lines

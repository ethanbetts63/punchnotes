# align_transcript.py
#
# Aligns a Whisper-generated transcript against a podscripts.co reference
# transcript of the same episode. The goal is to keep Whisper's pause-based
# line timing while borrowing podscripts' cleaner text.
#
# How it works
# ------------
# Both transcripts are flattened to word lists (bracket-only lines and tokens
# such as [MUSIC] / (laughter) are excluded from alignment but preserved in
# output). difflib.SequenceMatcher finds 1-for-1 word substitutions where the
# character-level similarity ratio meets a threshold (default 0.75). Accepted
# substitutions replace the Whisper word with the podscripts word in-place,
# leaving all line numbers and timestamps unchanged.
#
# Current limitations
# -------------------
# The approach is conservative but not perfect. False positives occur when:
#   - Both transcripts are wrong (neither is ground truth)
#   - Short words differ by one character but mean something completely
#     different (e.g. "bros" → "pros", "Food" → "Good", "tits" → "pits")
#   - Character similarity is high for structurally similar but semantically
#     unrelated words (e.g. "mathematically" → "dramatically")
#   - Tense / plurality differences that are both valid ("ruined" ↔ "ruin")
# Raising --threshold to 0.85+ reduces most short-word false positives but
# also drops some genuine proper-noun fixes. No single threshold is ideal.
#
# Future direction — domain translation file
# ------------------------------------------
# A more robust approach would be to run this alignment across many episodes,
# collect all close-match word pairs into a candidate file, and then pass that
# file to an LLM with a precise prompt: "identify only pairs where one word is
# always a transcription error for the other in this specific podcast context
# (e.g. Toney → Tony, Henchcliff → Hinchcliffe, H.E.B. is correct)."
#
# The resulting translation dictionary could then be applied as a deterministic
# pre-processing step to every transcript — no alignment needed, no false
# positives from short-word collisions — because the translations would be
# vetted to be unconditionally correct for Kill Tony specifically.
#
# This is left as future work.

import json
import re
import string
import time
from difflib import SequenceMatcher
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

BASE_URL = "https://podscripts.co"
PODCAST_PATH = "/podcasts/kill-tony"
TIMESTAMP_RE = re.compile(r"Starting point is (\d{1,2}):(\d{2}):(\d{2})")
EPISODE_NUM_RE = re.compile(r"#(\d+)")

# A line whose entire text is a bracket expression (e.g. "[MUSIC]", "(audience cheering)")
BRACKET_LINE_RE = re.compile(r"^\s*[\[\(].*[\]\)]\s*$")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def is_bracket_line(text: str) -> bool:
    return bool(BRACKET_LINE_RE.match(text.strip()))


def tokenize_line(text: str) -> list[tuple[str, str | None]]:
    """
    Split a line into (original_token, clean_token) pairs.

    clean_token is None for bracket tokens such as [MUSIC] or (laughs) — they
    are preserved verbatim in the output but excluded from alignment so they
    don't confuse the word-level diff.
    """
    result = []
    for token in text.split():
        # Bracket token: starts and ends with matching bracket characters
        if (token.startswith("[") and "]" in token) or (
            token.startswith("(") and ")" in token
        ):
            result.append((token, None))
        else:
            clean = token.strip(string.punctuation).lower()
            result.append((token, clean if clean else None))
    return result


class _Word:
    __slots__ = ("original", "clean", "line_idx", "word_idx")

    def __init__(self, original: str, clean: str, line_idx: int, word_idx: int):
        self.original = original
        self.clean = clean
        self.line_idx = line_idx
        self.word_idx = word_idx


def _build_word_list(lines: list[dict]) -> list[_Word]:
    words = []
    for line_idx, line in enumerate(lines):
        text = line.get("text", "")
        if is_bracket_line(text):
            continue
        for word_idx, (orig, clean) in enumerate(tokenize_line(text)):
            if clean is not None:
                words.append(_Word(orig, clean, line_idx, word_idx))
    return words


def hms_to_seconds(h: str, m: str, s: str) -> int:
    return int(h) * 3600 + int(m) * 60 + int(s)


def _fetch_podscripts_lines(
    episode_num: int, data_dir: Path, delay: float
) -> list[dict]:
    """
    Return podscripts transcript lines for the given episode number.
    Uses data/podscripts_index.json if available; otherwise crawls listing pages.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    # Try cached index first
    index_path = data_dir / "podscripts_index.json"
    path: str | None = None
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
        path = index.get(str(episode_num))

    # Fall back to live listing search (cap at 50 pages)
    if path is None:
        ep_str = str(episode_num)
        for page in range(1, 51):
            resp = session.get(
                f"{BASE_URL}{PODCAST_PATH}?page={page}", timeout=15
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select("h3 a[href]")
            if not links:
                break
            for a in links:
                m = EPISODE_NUM_RE.search(a.get_text())
                if m and m.group(1) == ep_str:
                    path = a["href"]
                    break
            if path:
                break
            time.sleep(delay)

    if path is None:
        raise ValueError(f"Episode #{episode_num} not found on podscripts.co")

    resp = session.get(f"{BASE_URL}{path}", timeout=20)
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
        if texts:
            lines.append(
                {"line_number": line_number, "text": " ".join(texts), "start": start}
            )
            line_number += 1

    return lines


def align_and_correct(
    whisper_lines: list[dict],
    pods_lines: list[dict],
    threshold: float,
) -> tuple[list[dict], dict]:
    """
    Align two transcripts of the same episode at word level and return
    a corrected copy of whisper_lines together with a stats dict.

    Only 1-for-1 word substitutions are made. A substitution is accepted when
    the character-level similarity of the two words meets `threshold`, which
    catches spelling errors and proper-noun garbling while rejecting genuine
    word-choice differences.
    """
    w_words = _build_word_list(whisper_lines)
    p_words = _build_word_list(pods_lines)

    matcher = SequenceMatcher(
        None,
        [w.clean for w in w_words],
        [p.clean for p in p_words],
        autojunk=False,
    )

    corrections: dict[tuple[int, int], str] = {}
    examples: list[tuple[str, str]] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "replace":
            continue
        # Only handle 1:1 swaps to stay conservative
        if (i2 - i1) != 1 or (j2 - j1) != 1:
            continue
        w = w_words[i1]
        p = p_words[j1]
        if w.clean == p.clean:
            continue
        sim = SequenceMatcher(None, w.clean, p.clean).ratio()
        if sim >= threshold:
            corrections[(w.line_idx, w.word_idx)] = p.original
            if len(examples) < 30:
                examples.append((w.original, p.original))

    corrected_lines = []
    for line_idx, line in enumerate(whisper_lines):
        text = line.get("text", "")
        if is_bracket_line(text):
            corrected_lines.append(line.copy())
            continue
        tokens = tokenize_line(text)
        rebuilt = [
            corrections.get((line_idx, wi), orig)
            for wi, (orig, _) in enumerate(tokens)
        ]
        corrected_lines.append({**line, "text": " ".join(rebuilt)})

    return corrected_lines, {
        "whisper_words": len(w_words),
        "pods_words": len(p_words),
        "substitutions": len(corrections),
        "examples": examples,
    }


def dump_episode(doc: dict) -> str:
    non_line = [(k, v) for k, v in doc.items() if k != "lines"]
    has_lines = "lines" in doc
    parts = ["{"]
    for i, (k, v) in enumerate(non_line):
        comma = "," if i < len(non_line) - 1 or has_lines else ""
        parts.append(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    if has_lines:
        parts.append('  "lines": [')
        for i, line in enumerate(doc["lines"]):
            comma = "," if i < len(doc["lines"]) - 1 else ""
            parts.append(f"    {json.dumps(line, ensure_ascii=False)}{comma}")
        parts.append("  ]")
    parts.append("}")
    return "\n".join(parts)


class Command(BaseCommand):
    help = (
        "Align a Whisper transcript against a podscripts.co transcript to correct "
        "spelling errors and proper-noun garbling while preserving Whisper's "
        "pause-based line timing."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--transcript",
            required=True,
            metavar="PATH",
            help="Path to Whisper transcript JSON (absolute or relative to BASE_DIR)",
        )
        parser.add_argument(
            "--episode",
            required=True,
            type=int,
            metavar="N",
            help="Kill Tony episode number (used to fetch the podscripts reference)",
        )
        parser.add_argument(
            "--output",
            default=None,
            metavar="PATH",
            help="Output path (default: {stem}_aligned.json alongside the input file)",
        )
        parser.add_argument(
            "--threshold",
            type=float,
            default=0.75,
            metavar="RATIO",
            help=(
                "Minimum character-similarity ratio for a word substitution "
                "(0–1, default 0.75). Lower catches more errors but risks false "
                "positives; higher is more conservative."
            ),
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.5,
            metavar="SECS",
            help="Pause between HTTP requests when crawling podscripts (default 1.5)",
        )

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"

        transcript_path = Path(options["transcript"])
        if not transcript_path.is_absolute():
            transcript_path = settings.BASE_DIR / transcript_path
        if not transcript_path.exists():
            self.stderr.write(self.style.ERROR(f"Not found: {transcript_path}"))
            return

        out_path = (
            Path(options["output"])
            if options["output"]
            else transcript_path.parent / f"{transcript_path.stem}_aligned.json"
        )

        # Load Whisper transcript
        whisper_doc = json.loads(transcript_path.read_text(encoding="utf-8"))
        whisper_lines = whisper_doc.get("lines", [])
        self.stdout.write(f"Whisper:     {len(whisper_lines)} lines  ({transcript_path.name})")

        # Fetch podscripts reference
        ep_num = options["episode"]
        self.stdout.write(f"Fetching podscripts reference for episode #{ep_num}...")
        try:
            pods_lines = _fetch_podscripts_lines(ep_num, data_dir, options["delay"])
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"podscripts fetch failed: {exc}"))
            return
        self.stdout.write(f"Podscripts:  {len(pods_lines)} lines")

        # Align
        self.stdout.write(f"Aligning at threshold={options['threshold']}...")
        corrected_lines, stats = align_and_correct(
            whisper_lines, pods_lines, threshold=options["threshold"]
        )

        # Report
        self.stdout.write(
            f"\nWhisper words:    {stats['whisper_words']}\n"
            f"Podscripts words: {stats['pods_words']}\n"
            f"Substitutions:    {stats['substitutions']}\n"
        )
        if stats["examples"]:
            self.stdout.write("Sample corrections (whisper → podscripts):")
            for w, p in stats["examples"]:
                self.stdout.write(f"  {w!r:30} → {p!r}")

        # Write
        out_doc = {**whisper_doc, "lines": corrected_lines}
        out_path.write_text(dump_episode(out_doc), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"\nWritten to {out_path}"))

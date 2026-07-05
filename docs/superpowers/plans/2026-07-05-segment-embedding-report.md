# Segment Embedding Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a second, parallel joke-similarity pipeline that embeds beats at the level of packed sentence-groups ("segments") instead of one vector per whole beat, so a reworded punchline buried in a different setup can still surface as a match — without touching the existing whole-beat embedding pipeline, so the two reports can be compared side by side.

**Architecture:** Mirrors the existing `generate` / `upload` / `update` three-command split beat-for-beat, but at segment granularity. A new pure-logic module (`pipeline/utils/segmenting.py`) splits a beat's raw transcript text (all lines in its range, regardless of `setup`/`punchline`/`tag`/`fluff` label) into sentences via a lightweight regex splitter, then greedily packs adjacent sentences into segments using a **minimum-word floor only — no maximum**: a segment closes the instant it reaches the floor, sentences below the floor accumulate into a still-open buffer (never re-opening an already-closed segment), and a trailing leftover below the floor merges backward into the previous segment. Each beat's segments are persisted once (build-once, like `search_text`) in a new `BeatSegment` table carrying their own `line_start`/`line_end` provenance. The embedding model is deliberately kept identical to the existing pipeline (`all-mpnet-base-v2`) so segmenting-vs-whole-beat is the only variable being tested. The new report aggregates by taking, for every cross-comedian beat pair within a `joke_type` group, the single best-matching segment pair — giving both a similarity score and the exact matching span as evidence.

**Tech Stack:** Django 6.0 management commands, MySQL via Django ORM, `sentence-transformers` (already a dev/local-machine dependency), stdlib `re` for sentence splitting (no new dependency), `numpy` for cosine similarity (already a dependency).

## Global Constraints

- Build this **in addition to** the existing whole-beat embedding pipeline — do not modify `pipeline/utils/generate/embeddings.py`, `pipeline/utils/update/embeddings.py`, `pipeline/utils/upload/embeddings.py`, or their `Beat.embedding`/`Beat.search_text` fields, except for the one explicitly-scoped refactor in Task 8 (extracting the shared JSON formatter — pure move, no behavior change).
- Segmentation must ignore the `label` field entirely (`setup`/`punchline`/`tag`/`fluff`) — pull every `Line` in a beat's `[line_start, line_end]` range regardless of label. This is a deliberate constraint: the whole point is to stop depending on line labels for search-text quality.
- No new Python dependencies. Sentence splitting is regex-based stdlib only; embedding still uses the already-available `sentence-transformers` (see `requirements-dev.txt`).
- Use the same embedding model (`all-mpnet-base-v2`) as the existing pipeline, so only the text-granularity variable changes between the two reports.
- The similarity threshold for the new report starts at the same `0.70` used today purely for a baseline comparison point — it is expected to need recalibration once real score distributions are visible, but that recalibration is out of scope for this build.
- No incremental-rebuild logic for the new report (the existing report's "only compare beats created since last run" logic is intentionally not replicated) — this is a first-cut experimental report for comparison, and full-rebuild-every-run is simpler and sufficient. Note this in code only via the absence of that logic, not via comments referencing "future work."
- Follow existing repo conventions exactly: outbox → upload → inbox → update → archive; `--archive` flag support; `Log` wrapper; `django_assert_num_queries`-style query care; `bulk_create`/`bulk_update` for batch writes.

---

## File Structure

| File | Responsibility |
|---|---|
| `pipeline/utils/segmenting.py` | Pure logic: sentence splitting + greedy min-word packing. No DB access. |
| `pipeline/models/beat_segment.py` | `BeatSegment` model. |
| `pipeline/models/__init__.py` | Register `BeatSegment` (modify). |
| `pipeline/admin.py` | Register `BeatSegment` admin (modify). |
| `pipeline/migrations/0005_beatsegment.py` | Schema migration (generated via `makemigrations`). |
| `pipeline/utils/update/segment_embeddings.py` | Server-side: build+persist segments for beats missing them, list segments needing embeddings, ingest uploaded embeddings. |
| `api/views/pipeline.py` | Add `UnsegmentedBeatSegmentsView`, `SegmentEmbeddingsView` (modify). |
| `api/urls_pipeline.py` | Wire the two new endpoints (modify). |
| `pipeline/utils/generate/segment_embeddings.py` | Local machine: fetch unsegmented-beat-segments, embed, write to outbox. |
| `pipeline/utils/upload/segment_embeddings.py` | Local machine: POST outbox files to server inbox. |
| `pipeline/management/commands/generate.py` | Add `--segment_embeddings` and `--segment_embeddings_report` flags (modify). |
| `pipeline/management/commands/upload.py` | Add `--segment_embeddings` flag (modify). |
| `pipeline/management/commands/update.py` | Add `--segment_embeddings` flag (modify). |
| `pipeline/utils/report_format.py` | Shared JSON pretty-printer, extracted from `embeddings_report.py`. |
| `pipeline/utils/generate/embeddings_report.py` | Use the extracted formatter instead of its own private copy (modify, behavior-preserving). |
| `pipeline/utils/generate/segment_embeddings_report.py` | Segment-level similarity report generator. |
| `pipeline/management/commands/reset_db.py` | Restore `segment_embeddings_archive/` on reset (modify). |
| `pipeline/data_private/.gitignore` | Track the new archive dir and report file (modify). |
| `docs/pipeline.md` | Document the new parallel flow (modify). |

---

### Task 1: Sentence splitting and greedy min-word packing (pure logic)

**Files:**
- Create: `pipeline/utils/segmenting.py`
- Test: `pipeline/tests/utils/test_segmenting.py`

**Interfaces:**
- Produces: `Segment` (frozen dataclass: `text: str`, `line_start: int`, `line_end: int`), `segment_beat_lines(lines: list[tuple[int, str]], min_words: int = DEFAULT_MIN_SEGMENT_WORDS) -> list[Segment]`, `DEFAULT_MIN_SEGMENT_WORDS: int`. `lines` is a list of `(line_number, text)` tuples in ascending line order, already restricted to a single beat's `[line_start, line_end]` range, with **no label filtering** — the caller passes every line in range.

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/utils/test_segmenting.py
from pipeline.utils.segmenting import Segment, segment_beat_lines


def test_empty_lines_returns_no_segments():
    assert segment_beat_lines([], min_words=10) == []


def test_single_short_beat_returns_one_undersized_segment():
    lines = [(1, "Hi there everyone.")]
    result = segment_beat_lines(lines, min_words=10)
    assert result == [Segment(text="Hi there everyone.", line_start=1, line_end=1)]


def test_sentence_at_or_above_min_closes_immediately():
    # Sentence 1 alone already meets min_words -> closes on its own.
    lines = [(1, "This sentence right here has plenty of words in it.")]
    result = segment_beat_lines(lines, min_words=5)
    assert result == [
        Segment(text="This sentence right here has plenty of words in it.", line_start=1, line_end=1)
    ]


def test_two_short_sentences_after_a_closed_one_combine_together():
    # s1 alone >= min -> closes. s2 alone < min -> stays open. s3 joins s2 -> crosses min -> closes.
    # This is the exact edge case: s3 must NOT get appended to the already-closed s1.
    lines = [
        (1, "First sentence closes here on its own already."),
        (2, "Short one."),
        (3, "Another short bit."),
    ]
    result = segment_beat_lines(lines, min_words=4)
    assert result == [
        Segment(text="First sentence closes here on its own already.", line_start=1, line_end=1),
        Segment(text="Short one. Another short bit.", line_start=2, line_end=3),
    ]


def test_trailing_short_leftover_merges_into_previous_segment():
    lines = [
        (1, "First sentence closes here on its own already."),
        (2, "Tiny."),
    ]
    result = segment_beat_lines(lines, min_words=4)
    assert result == [
        Segment(text="First sentence closes here on its own already. Tiny.", line_start=1, line_end=2)
    ]


def test_sentence_split_across_two_transcript_lines_stays_one_segment():
    # No terminal punctuation until the end of line 2 -> one sentence spanning both lines.
    lines = [
        (10, "And now we are proud to announce we are going back to Madison Square Garden for the third"),
        (11, "year in a row completely unprecedented, the world's greatest arena."),
    ]
    result = segment_beat_lines(lines, min_words=5)
    assert len(result) == 1
    assert result[0].line_start == 10
    assert result[0].line_end == 11
    assert "Madison Square Garden" in result[0].text
    assert "greatest arena" in result[0].text


def test_abbreviation_with_no_following_capital_does_not_force_a_split():
    lines = [(1, "The show starts at 10 a.m. sharp and ends at 10 p.m. tonight.")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].text == "The show starts at 10 a.m. sharp and ends at 10 p.m. tonight."


def test_known_title_abbreviation_does_not_split_before_proper_noun():
    # min_words=1 makes every real sentence close on its own, so segment count == sentence count,
    # which lets us directly assert the sentence splitter didn't break after "Mr."
    lines = [(1, "Mr. Smith walked in. He said hello.")]
    result = segment_beat_lines(lines, min_words=1)
    assert len(result) == 2
    assert result[0].text == "Mr. Smith walked in."
    assert result[1].text == "He said hello."


def test_no_terminal_punctuation_is_treated_as_one_sentence():
    lines = [(1, "we ran a long line here with no punctuation at all whatsoever")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].text == "we ran a long line here with no punctuation at all whatsoever"


def test_blank_lines_are_skipped():
    lines = [(1, ""), (2, "  "), (3, "Real content finally shows up here.")]
    result = segment_beat_lines(lines, min_words=3)
    assert len(result) == 1
    assert result[0].line_start == 3
    assert result[0].line_end == 3
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest pipeline/tests/utils/test_segmenting.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.utils.segmenting'`

- [ ] **Step 3: Implement the segmentation module**

```python
# pipeline/utils/segmenting.py
import re
from dataclasses import dataclass

DEFAULT_MIN_SEGMENT_WORDS = 12

# Trailing word before a `.!?` that should NOT be treated as a sentence end,
# even when the following word happens to be capitalized (e.g. "Mr. Smith").
_ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "st", "vs", "etc", "jr", "sr", "prof", "rev"}

# A sentence boundary is punctuation followed by whitespace and then something
# that looks like the start of a new sentence (capital letter, digit, quote, bracket).
# This naturally avoids most false splits inside abbreviations like "a.m." or "p.m.",
# since the text immediately following is normally lowercase continuation.
_SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\[(])')


@dataclass(frozen=True)
class Segment:
    text: str
    line_start: int
    line_end: int


@dataclass(frozen=True)
class _Sentence:
    text: str
    line_start: int
    line_end: int
    word_count: int


def _join_lines(lines: list[tuple[int, str]]) -> tuple[str, list[tuple[int, int, int]]]:
    """Join line texts with single spaces; return joined text and per-line (start, end, line_number) offsets."""
    parts = []
    offsets = []
    cursor = 0
    for line_number, text in lines:
        text = text.strip()
        if not text:
            continue
        start = cursor
        parts.append(text)
        cursor += len(text)
        offsets.append((start, cursor, line_number))
        cursor += 1  # account for the joining space
    return " ".join(parts), offsets


def _line_range_for_span(offsets: list[tuple[int, int, int]], span_start: int, span_end: int) -> tuple[int, int]:
    matching = [line_number for start, end, line_number in offsets if end > span_start and start < span_end]
    return (min(matching), max(matching))


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    boundaries = []
    for match in _SENTENCE_SPLIT_RE.finditer(text):
        preceding_words = re.findall(r"[A-Za-z]+", text[:match.start()])
        if preceding_words and preceding_words[-1].lower() in _ABBREVIATIONS:
            continue
        boundaries.append((match.start(), match.end()))

    spans = []
    start = 0
    for split_start, split_end in boundaries:
        spans.append((start, split_start))
        start = split_end
    spans.append((start, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def segment_beat_lines(lines: list[tuple[int, str]], min_words: int = DEFAULT_MIN_SEGMENT_WORDS) -> list[Segment]:
    full_text, offsets = _join_lines(lines)
    if not full_text:
        return []

    sentences = []
    for span_start, span_end in _sentence_spans(full_text):
        sentence_text = full_text[span_start:span_end].strip()
        line_start, line_end = _line_range_for_span(offsets, span_start, span_end)
        sentences.append(_Sentence(
            text=sentence_text,
            line_start=line_start,
            line_end=line_end,
            word_count=len(sentence_text.split()),
        ))

    segments: list[Segment] = []
    buffer_parts: list[str] = []
    buffer_line_start = None
    buffer_line_end = None
    buffer_words = 0

    for sentence in sentences:
        if not buffer_parts:
            buffer_line_start = sentence.line_start
        buffer_parts.append(sentence.text)
        buffer_line_end = sentence.line_end
        buffer_words += sentence.word_count

        if buffer_words >= min_words:
            segments.append(Segment(text=" ".join(buffer_parts), line_start=buffer_line_start, line_end=buffer_line_end))
            buffer_parts = []
            buffer_words = 0

    if buffer_parts:
        leftover_text = " ".join(buffer_parts)
        if segments:
            previous = segments[-1]
            segments[-1] = Segment(text=f"{previous.text} {leftover_text}", line_start=previous.line_start, line_end=buffer_line_end)
        else:
            segments.append(Segment(text=leftover_text, line_start=buffer_line_start, line_end=buffer_line_end))

    return segments
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest pipeline/tests/utils/test_segmenting.py -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/utils/segmenting.py pipeline/tests/utils/test_segmenting.py
git commit -m "feat: add sentence-splitting and greedy min-word segment packing"
```

---

### Task 2: `BeatSegment` model

**Files:**
- Create: `pipeline/models/beat_segment.py`
- Modify: `pipeline/models/__init__.py`
- Modify: `pipeline/admin.py`
- Create: `pipeline/migrations/0005_beatsegment.py` (via `makemigrations`)
- Test: `pipeline/tests/models/test_beat_segment.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `BeatSegment` model with fields `beat` (FK to `Beat`, `related_name="segments"`), `ordinal` (int, 1-indexed), `text`, `line_start`, `line_end`, `embedding` (JSONField, default `[]`), `created_at`. `unique_together = [["beat", "ordinal"]]`.

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/models/test_beat_segment.py
import pytest
from django.db import IntegrityError

pytestmark = pytest.mark.django_db


def test_beat_segment_defaults_and_str(full_set):
    from pipeline.models import BeatSegment

    segment = BeatSegment.objects.create(
        beat=full_set["beat"], ordinal=1, text="I used to be an astronaut.",
        line_start=1, line_end=1,
    )

    assert segment.embedding == []
    assert str(segment) == f"{full_set['beat']} – segment 1"
    assert full_set["beat"].segments.count() == 1


def test_beat_segment_ordinal_is_unique_per_beat(full_set):
    from pipeline.models import BeatSegment

    BeatSegment.objects.create(beat=full_set["beat"], ordinal=1, text="a", line_start=1, line_end=1)
    with pytest.raises(IntegrityError):
        BeatSegment.objects.create(beat=full_set["beat"], ordinal=1, text="b", line_start=2, line_end=2)
```

Note: this test relies on the `full_set` fixture already defined in `api/tests/conftest.py`. Add a `pipeline/tests/models/conftest.py` re-exporting it (pytest fixtures aren't shared across app test dirs by default):

```python
# pipeline/tests/models/conftest.py
from api.tests.conftest import full_set  # noqa: F401
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/models/test_beat_segment.py -v`
Expected: FAIL with `ImportError: cannot import name 'BeatSegment' from 'pipeline.models'`

- [ ] **Step 3: Create the model**

```python
# pipeline/models/beat_segment.py
from django.db import models


class BeatSegment(models.Model):
    beat = models.ForeignKey('pipeline.Beat', on_delete=models.CASCADE, related_name='segments')
    ordinal = models.PositiveSmallIntegerField()
    text = models.TextField()
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()
    embedding = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['beat', 'ordinal']
        unique_together = [['beat', 'ordinal']]

    def __str__(self):
        return f"{self.beat} – segment {self.ordinal}"
```

```python
# pipeline/models/__init__.py
from pipeline.models.comedian import Comedian
from pipeline.models.video import Video
from pipeline.models.set import Set
from pipeline.models.line import Line
from pipeline.models.bit import Bit
from pipeline.models.beat import Beat
from pipeline.models.beat_segment import BeatSegment

__all__ = ['Comedian', 'Video', 'Set', 'Line', 'Bit', 'Beat', 'BeatSegment']
```

Add to `pipeline/admin.py` (after the existing `BeatAdmin` registration):

```python
from pipeline.models import Comedian, Video, Set, Line, Bit, Beat, BeatSegment
```

```python
@admin.register(BeatSegment)
class BeatSegmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'beat', 'ordinal', 'line_start', 'line_end')
    search_fields = ('text',)
    raw_id_fields = ('beat',)
```

Generate the migration:

Run: `python manage.py makemigrations pipeline`
Expected: Creates `pipeline/migrations/0005_beatsegment.py` containing a `CreateModel` for `BeatSegment` with fields `id`, `ordinal`, `text`, `line_start`, `line_end`, `embedding`, `created_at`, `beat` (FK to `pipeline.beat`, `on_delete=CASCADE`, `related_name="segments"`), plus an `AlterUniqueTogether` for `("beat", "ordinal")`. Inspect the generated file to confirm these fields are present — do not hand-edit it.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python manage.py migrate pipeline && pytest pipeline/tests/models/test_beat_segment.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/models/beat_segment.py pipeline/models/__init__.py pipeline/admin.py pipeline/migrations/0005_beatsegment.py pipeline/tests/models/test_beat_segment.py pipeline/tests/models/conftest.py
git commit -m "feat: add BeatSegment model"
```

---

### Task 3: Build, list, and ingest segment embeddings (server-side logic)

**Files:**
- Create: `pipeline/utils/update/segment_embeddings.py`
- Test: `pipeline/tests/utils/update/test_segment_embeddings.py`

**Interfaces:**
- Consumes: `segment_beat_lines`, `DEFAULT_MIN_SEGMENT_WORDS` from `pipeline.utils.segmenting` (Task 1); `Beat`, `BeatSegment`, `Line` from `pipeline.models` (Task 2); `run_inbox_update` from `pipeline.utils.inbox`; `Log` from `pipeline.log`.
- Produces: `ensure_beat_segments(beats: list[Beat]) -> None`, `unembedded_beat_segments() -> list[dict]` (each `{"key": str, "text": str}`), `ingest_segment_embeddings(pairs: list[dict]) -> dict` (`{"stored": int, "not_found": int, "invalid_key": int}`), `run_update_segment_embeddings(log: Log, archive: bool = False) -> None`. Key format: `ep{episode}.set{set:02d}.bit{bit:03d}.beat{beat:03d}.seg{ordinal:03d}`.

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/utils/update/test_segment_embeddings.py
import pytest

from pipeline.models import Beat, BeatSegment, Bit, Comedian, Line, Set, Video

pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number, video_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", number=video_number, title=f"Episode {slug}", url=f"https://example.com/{slug}")
    return Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10))


def _make_beat(standup_set, bit_num, beat_num, line_start, line_end, joke_type="misdirect"):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit_{bit_num:03d}", line_start=line_start, line_end=line_end)
    return Beat.objects.create(
        bit=bit, beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
        line_start=line_start, line_end=line_end, joke_type=joke_type,
    )


def test_ensure_beat_segments_creates_rows_for_new_beats():
    from pipeline.utils.update.segment_embeddings import ensure_beat_segments

    standup_set = _make_set("Comic One", "comic-one", 1, 100)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="This is the punchline right here today.", start_seconds=1.0)

    ensure_beat_segments([beat])

    segments = list(beat.segments.order_by("ordinal"))
    assert len(segments) == 1
    assert segments[0].ordinal == 1
    assert segments[0].text == "This is the punchline right here today."


def test_ensure_beat_segments_skips_beats_that_already_have_segments():
    from pipeline.utils.update.segment_embeddings import ensure_beat_segments

    standup_set = _make_set("Comic One", "comic-one-2", 1, 101)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Original stored text.", start_seconds=1.0)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="manually seeded", line_start=1, line_end=1)

    ensure_beat_segments([beat])

    assert list(beat.segments.values_list("text", flat=True)) == ["manually seeded"]


def test_unembedded_beat_segments_builds_and_returns_missing_keys():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-3", 2, 102)
    beat = _make_beat(standup_set, 3, 4, 5, 5)
    Line.objects.create(set=standup_set, line_number=5, label="punchline", text="A single punchline segment.", start_seconds=1.0)

    result = unembedded_beat_segments()

    assert result == [{"key": "ep102.set02.bit003.beat004.seg001", "text": "A single punchline segment."}]
    assert Beat.objects.get(id=beat.id).segments.count() == 1


def test_unembedded_beat_segments_excludes_beats_without_joke_type():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-4", 1, 103)
    _make_beat(standup_set, 1, 1, 1, 1, joke_type="")
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Untyped beat text.", start_seconds=1.0)

    assert unembedded_beat_segments() == []


def test_unembedded_beat_segments_excludes_already_embedded_segments():
    from pipeline.utils.update.segment_embeddings import unembedded_beat_segments

    standup_set = _make_set("Comic One", "comic-one-5", 1, 104)
    beat = _make_beat(standup_set, 1, 1, 1, 1)
    Line.objects.create(set=standup_set, line_number=1, label="punchline", text="Already embedded text.", start_seconds=1.0)
    BeatSegment.objects.create(beat=beat, ordinal=1, text="Already embedded text.", line_start=1, line_end=1, embedding=[1.0, 0.0])

    assert unembedded_beat_segments() == []


def test_ingest_segment_embeddings_stores_by_key():
    from pipeline.utils.update.segment_embeddings import ingest_segment_embeddings

    standup_set = _make_set("Comic One", "comic-one-6", 2, 105)
    beat = _make_beat(standup_set, 3, 4, 1, 1)
    segment = BeatSegment.objects.create(beat=beat, ordinal=1, text="text", line_start=1, line_end=1)

    result = ingest_segment_embeddings([
        {"key": "ep105.set02.bit003.beat004.seg001", "embedding": [1.0, 2.0]},
    ])

    segment.refresh_from_db()
    assert result == {"stored": 1, "not_found": 0, "invalid_key": 0}
    assert segment.embedding == [1.0, 2.0]


def test_ingest_segment_embeddings_reports_not_found_and_invalid_key():
    from pipeline.utils.update.segment_embeddings import ingest_segment_embeddings

    result = ingest_segment_embeddings([
        {"key": "ep999.set01.bit001.beat001.seg001", "embedding": [1.0]},
        {"key": "not-a-real-key", "embedding": [1.0]},
    ])

    assert result == {"stored": 0, "not_found": 1, "invalid_key": 1}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest pipeline/tests/utils/update/test_segment_embeddings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.utils.update.segment_embeddings'`

- [ ] **Step 3: Implement the module**

```python
# pipeline/utils/update/segment_embeddings.py
import json
import re
from pathlib import Path

from django.conf import settings

from pipeline.log import Log
from pipeline.models import Beat, BeatSegment, Line
from pipeline.utils.inbox import run_inbox_update
from pipeline.utils.segmenting import segment_beat_lines


def _load_all_lines_by_set(beats: list) -> dict:
    set_ids = {beat.bit.set_id for beat in beats}
    if not set_ids:
        return {}
    lines_by_set: dict = {}
    lines = (
        Line.objects
        .filter(set_id__in=set_ids)
        .order_by("set_id", "line_number")
        .values_list("set_id", "line_number", "text")
    )
    for set_id, line_number, text in lines:
        lines_by_set.setdefault(set_id, []).append((line_number, text))
    return lines_by_set


def ensure_beat_segments(beats: list) -> None:
    """Build and persist BeatSegment rows for any beat that doesn't have any yet."""
    beats = list(beats)
    if not beats:
        return

    already_segmented = set(
        BeatSegment.objects
        .filter(beat_id__in=[beat.id for beat in beats])
        .values_list("beat_id", flat=True)
        .distinct()
    )
    beats = [beat for beat in beats if beat.id not in already_segmented]
    if not beats:
        return

    lines_by_set = _load_all_lines_by_set(beats)
    segments_to_create = []
    for beat in beats:
        set_id = beat.bit.set_id
        beat_lines = [
            (line_number, text)
            for line_number, text in lines_by_set.get(set_id, [])
            if beat.line_start <= line_number <= beat.line_end
        ]
        for ordinal, segment in enumerate(segment_beat_lines(beat_lines), start=1):
            segments_to_create.append(BeatSegment(
                beat=beat, ordinal=ordinal, text=segment.text,
                line_start=segment.line_start, line_end=segment.line_end,
            ))

    BeatSegment.objects.bulk_create(segments_to_create)


def _parse_segment_key(key: str) -> dict | None:
    m = re.fullmatch(r"ep(\d+)\.set(\d+)\.bit(\d+)\.beat(\d+)\.seg(\d+)", key)
    if not m:
        return None
    return {
        "episode_number": int(m.group(1)),
        "set_number": int(m.group(2)),
        "bit_number": int(m.group(3)),
        "beat_number": int(m.group(4)),
        "segment_ordinal": int(m.group(5)),
    }


def unembedded_beat_segments() -> list[dict]:
    beats = list(
        Beat.objects
        .exclude(joke_type=None)
        .exclude(joke_type="")
        .select_related("bit__set__video")
        .only(
            "id", "beat_id", "line_start", "line_end", "joke_type",
            "bit__bit_id", "bit__set_id",
            "bit__set__set_number", "bit__set__video__number",
        )
        .order_by("bit__set__video__number", "bit__set__set_number")
    )
    if not beats:
        return []

    ensure_beat_segments(beats)

    result = []
    segments = (
        BeatSegment.objects
        .filter(beat__in=beats, embedding=[])
        .select_related("beat__bit__set__video")
        .order_by("beat__bit__set__video__number", "beat__bit__set__set_number", "beat_id", "ordinal")
    )
    for segment in segments:
        beat = segment.beat
        set_obj = beat.bit.set
        ep_num = set_obj.video.number
        set_num = set_obj.set_number
        bit_m = re.search(r"(\d+)$", beat.bit.bit_id)
        beat_m = re.search(r"(\d+)$", beat.beat_id)
        if not bit_m or not beat_m:
            continue
        key = (
            f"ep{ep_num}.set{set_num:02d}.bit{int(bit_m.group(1)):03d}"
            f".beat{int(beat_m.group(1)):03d}.seg{segment.ordinal:03d}"
        )
        result.append({"key": key, "text": segment.text})
    return result


def ingest_segment_embeddings(pairs: list[dict]) -> dict:
    stored = not_found = invalid_key = 0
    updates = []
    for pair in pairs:
        parsed = _parse_segment_key(pair.get("key", ""))
        if parsed is None:
            invalid_key += 1
            continue
        bit_id = f"bit_{parsed['bit_number']:03d}"
        beat_id = f"bit_{parsed['bit_number']:03d}_beat_{parsed['beat_number']:03d}"
        try:
            segment = BeatSegment.objects.get(
                ordinal=parsed["segment_ordinal"],
                beat__beat_id=beat_id,
                beat__bit__bit_id=bit_id,
                beat__bit__set__set_number=parsed["set_number"],
                beat__bit__set__video__number=parsed["episode_number"],
            )
            segment.embedding = pair.get("embedding", [])
            updates.append(segment)
        except BeatSegment.DoesNotExist:
            not_found += 1
    if updates:
        BeatSegment.objects.bulk_update(updates, ["embedding"], batch_size=500)
        stored = len(updates)
    return {"stored": stored, "not_found": not_found, "invalid_key": invalid_key}


def _process_segment_embeddings_file(path: Path) -> dict:
    pairs = []
    invalid_key = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            pairs.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_key += 1
    result = ingest_segment_embeddings(pairs)
    result["invalid_key"] += invalid_key
    return result


def run_update_segment_embeddings(log: Log, archive: bool = False) -> None:
    if archive:
        source_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive"
        if not source_dir.exists():
            log("No segment_embeddings_archive/ dir.")
            return
        files = sorted(source_dir.glob("*.jsonl"))
        if not files:
            log("No files in segment_embeddings_archive/")
            return
        for path in files:
            result = _process_segment_embeddings_file(path)
            log(f"  {path.name}: {result['stored']} stored, {result['not_found']} not found")
        log.success(f"Done. {len(files)} file(s) processed.")
    else:
        run_inbox_update(
            inbox_dir=settings.PIPELINE_DATA_DIR / "segment_embeddings_inbox",
            archive_dir=settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive",
            process_fn=_process_segment_embeddings_file,
            log=log,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest pipeline/tests/utils/update/test_segment_embeddings.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/utils/update/segment_embeddings.py pipeline/tests/utils/update/test_segment_embeddings.py
git commit -m "feat: build, list, and ingest beat segment embeddings server-side"
```

---

### Task 4: API endpoints

**Files:**
- Modify: `api/views/pipeline.py`
- Modify: `api/urls_pipeline.py`
- Test: `api/tests/views/test_segment_embeddings.py`

**Interfaces:**
- Consumes: `unembedded_beat_segments` from `pipeline.utils.update.segment_embeddings` (Task 3).
- Produces: `GET /api/pipeline/unsegmented-beat-segments/` → `{"segments": [...]}`; `POST /api/pipeline/segment-embeddings/` → writes to `segment_embeddings_inbox/`, returns `{"status": "queued", "file": ...}` with status 202.

- [ ] **Step 1: Write the failing tests**

```python
# api/tests/views/test_segment_embeddings.py
import json

import pytest
from django.test import override_settings

pytestmark = pytest.mark.django_db


def test_unsegmented_beat_segments_view_returns_segments(api_client, full_set):
    resp = api_client.get("/api/pipeline/unsegmented-beat-segments/")

    assert resp.status_code == 200
    segments = resp.json()["segments"]
    assert len(segments) == 1
    assert segments[0]["key"].endswith(".seg001")


def test_segment_embeddings_view_writes_inbox_file(api_client, tmp_path):
    payload = json.dumps({"key": "ep700.set01.bit001.beat001.seg001", "embedding": [1.0, 2.0]}) + "\n"

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        resp = api_client.post(
            "/api/pipeline/segment-embeddings/",
            data=payload.encode("utf-8"),
            content_type="application/x-ndjson",
        )

    assert resp.status_code == 202
    files = list((tmp_path / "segment_embeddings_inbox").glob("*.jsonl"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8") == payload
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest api/tests/views/test_segment_embeddings.py -v`
Expected: FAIL with 404 (routes don't exist yet)

- [ ] **Step 3: Add the views and routes**

Add to `api/views/pipeline.py` (after `EmbeddingsView`):

```python
class UnsegmentedBeatSegmentsView(PipelineView):
    def get(self, request):
        from pipeline.utils.update.segment_embeddings import unembedded_beat_segments
        return Response({"segments": unembedded_beat_segments()})


class SegmentEmbeddingsView(PipelineView):
    def post(self, request):
        inbox_dir = settings.PIPELINE_DATA_DIR / "segment_embeddings_inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        dest = inbox_dir / f"segment_embeddings_{ts}_{uuid.uuid4().hex[:8]}.jsonl"
        content = request.body
        dest.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return Response({"status": "queued", "file": dest.name}, status=202)
```

Update `api/urls_pipeline.py`:

```python
from django.urls import path

from api.views.pipeline import (
    AnnotatedSetBatchView,
    AnnotatedSetView,
    AudioHistoryView,
    ComedianAliasesView,
    ComedianCandidatesView,
    EmbeddingsView,
    MissingSetImagesView,
    SegmentEmbeddingsView,
    SetImageBatchView,
    UnembeddedBeatsView,
    UnsegmentedBeatSegmentsView,
    VideoScrapeQueueView,
    VideoScrapeResultView,
)

urlpatterns = [
    path("annotated-set/", AnnotatedSetView.as_view()),
    path("annotated-set-batch/", AnnotatedSetBatchView.as_view()),
    path("audio-history/", AudioHistoryView.as_view()),
    path("comedian-candidates/", ComedianCandidatesView.as_view()),
    path("comedian-aliases/", ComedianAliasesView.as_view()),
    path("missing-set-images/", MissingSetImagesView.as_view()),
    path("set-images-batch/", SetImageBatchView.as_view()),
    path("unembedded-beats/", UnembeddedBeatsView.as_view()),
    path("embeddings/", EmbeddingsView.as_view()),
    path("unsegmented-beat-segments/", UnsegmentedBeatSegmentsView.as_view()),
    path("segment-embeddings/", SegmentEmbeddingsView.as_view()),
    path("videos-to-scrape/", VideoScrapeQueueView.as_view()),
    path("video-scrape-result/", VideoScrapeResultView.as_view()),
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest api/tests/views/test_segment_embeddings.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add api/views/pipeline.py api/urls_pipeline.py api/tests/views/test_segment_embeddings.py
git commit -m "feat: add unsegmented-beat-segments and segment-embeddings endpoints"
```

---

### Task 5: `generate --segment_embeddings` command

**Files:**
- Create: `pipeline/utils/generate/segment_embeddings.py`
- Modify: `pipeline/management/commands/generate.py`
- Test: `pipeline/tests/utils/generate/test_segment_embeddings.py`

**Interfaces:**
- Consumes: `pipeline_session`, `server_url` from `pipeline.utils.http`; `Log` from `pipeline.log`.
- Produces: `generate_segment_embeddings(options: dict, log: Log) -> None`. Writes `segment_embeddings_{ts}.jsonl` to `settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox"`.

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/utils/generate/test_segment_embeddings.py
import json

from pipeline.utils.generate import segment_embeddings


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, payload):
        self._payload = payload

    def get(self, url):
        return FakeResponse(self._payload)


class FakeModel:
    def encode(self, texts, batch_size, show_progress_bar):
        return [[float(len(t)), 0.0] for t in texts]


def test_generate_segment_embeddings_writes_outbox_file(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    segments_payload = {"segments": [{"key": "ep1.set01.bit001.beat001.seg001", "text": "hello world"}]}
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession(segments_payload))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    import sentence_transformers
    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", lambda name, **kwargs: FakeModel())

    log = CapturingLog()
    segment_embeddings.generate_segment_embeddings({}, log)

    files = list((tmp_path / "segment_embeddings_outbox").glob("*.jsonl"))
    assert len(files) == 1
    line = json.loads(files[0].read_text(encoding="utf-8").splitlines()[0])
    assert line["key"] == "ep1.set01.bit001.beat001.seg001"
    assert line["embedding"] == [11.0, 0.0]
    assert "Written 1 segment embeddings" in log.messages[-1]


def test_generate_segment_embeddings_no_segments_logs_and_returns(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession({"segments": []}))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    log = CapturingLog()
    segment_embeddings.generate_segment_embeddings({}, log)

    assert log.messages == ["No beat segments need embeddings."]
    assert not (tmp_path / "segment_embeddings_outbox").exists()


def test_generate_segment_embeddings_rejects_invalid_batch_size(tmp_path, monkeypatch, settings):
    settings.PIPELINE_DATA_DIR = tmp_path
    segments_payload = {"segments": [{"key": "ep1.set01.bit001.beat001.seg001", "text": "hi"}]}
    monkeypatch.setattr(segment_embeddings, "pipeline_session", lambda: FakeSession(segments_payload))
    monkeypatch.setattr(segment_embeddings, "server_url", lambda path: f"https://example.test{path}")

    import pytest
    with pytest.raises(ValueError, match="--batch-size must be at least 1"):
        segment_embeddings.generate_segment_embeddings({"batch_size": 0}, CapturingLog())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest pipeline/tests/utils/generate/test_segment_embeddings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.utils.generate.segment_embeddings'`

- [ ] **Step 3: Implement**

```python
# pipeline/utils/generate/segment_embeddings.py
import json
from datetime import datetime, timezone

from django.conf import settings

from pipeline.utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_segment_embeddings(options: dict, log: Log) -> None:
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/unsegmented-beat-segments/"))
    resp.raise_for_status()
    segments = resp.json().get("segments", [])

    if not segments:
        log("No beat segments need embeddings.")
        return

    log(f"{len(segments)} segment(s) to embed. Loading model...")
    from sentence_transformers import SentenceTransformer

    model_kwargs = {}
    if options.get("device"):
        model_kwargs["device"] = options["device"]
    model = SentenceTransformer("all-mpnet-base-v2", **model_kwargs)

    batch_size = options.get("batch_size") or 32
    if batch_size < 1:
        raise ValueError("--batch-size must be at least 1")

    log(f"Encoding {len(segments)} text(s) with batch size {batch_size}...")
    embeddings = model.encode([s["text"] for s in segments], batch_size=batch_size, show_progress_bar=True).tolist()

    outbox_dir = settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = outbox_dir / f"segment_embeddings_{ts}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for segment, embedding in zip(segments, embeddings):
            f.write(json.dumps({"key": segment["key"], "embedding": embedding}, separators=(",", ":")) + "\n")

    log.success(f"Written {len(segments)} segment embeddings to {out_path.name}")
```

Note: the test monkeypatches `sentence_transformers.SentenceTransformer` directly (not `segment_embeddings.SentenceTransformer`) because the real code imports it lazily inside the function body — same pattern as the existing `generate_embeddings`, so `.tolist()` on the fake model's return value must work too. Adjust `FakeModel.encode` to return an object with `.tolist()` if the plain-list monkeypatch above doesn't satisfy that; a plain Python list already has no `.tolist()`, so make `FakeModel.encode` return `[[float(len(t)), 0.0] for t in texts]` wrapped so `.tolist()` works — simplest fix is for the fake to return `numpy.array(...)`:

```python
# Adjust FakeModel in the test file:
import numpy as np


class FakeModel:
    def encode(self, texts, batch_size, show_progress_bar):
        return np.array([[float(len(t)), 0.0] for t in texts])
```

Update the test file's `FakeModel` accordingly before running.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest pipeline/tests/utils/generate/test_segment_embeddings.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Wire the command flag**

Modify `pipeline/management/commands/generate.py` — add to the mutually exclusive group (after `--embeddings`):

```python
        group.add_argument("--segment_embeddings", action="store_true", help="Compute segment-level beat embeddings and write to segment_embeddings_outbox/")
```

Update the `--local` help text to mention it, and add dispatch (after the `--embeddings` branch):

```python
        parser.add_argument("--local", action="store_true", help="Target local dev server (applies to: --audio, --comedian_aliases, --set_images, --embeddings, --segment_embeddings)")
```

```python
        elif options["segment_embeddings"]:
            from pipeline.utils.generate.segment_embeddings import generate_segment_embeddings
            generate_segment_embeddings(options, log)
```

- [ ] **Step 6: Commit**

```bash
git add pipeline/utils/generate/segment_embeddings.py pipeline/tests/utils/generate/test_segment_embeddings.py pipeline/management/commands/generate.py
git commit -m "feat: add generate --segment_embeddings command"
```

---

### Task 6: `upload --segment_embeddings` command

**Files:**
- Create: `pipeline/utils/upload/segment_embeddings.py`
- Modify: `pipeline/management/commands/upload.py`
- Test: `pipeline/tests/utils/upload/test_segment_embeddings.py`

**Interfaces:**
- Consumes: `upload_jsonl_files_chunked` from `pipeline.utils.http` (existing, unmodified).
- Produces: `upload_segment_embeddings(options: dict, log: Log) -> None`.

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/utils/upload/test_segment_embeddings.py
from pipeline.utils.upload import segment_embeddings


class CapturingLog:
    def __call__(self, msg):
        pass

    def success(self, msg):
        pass

    def error(self, msg):
        pass


def test_upload_segment_embeddings_uses_correct_dirs_and_endpoint(monkeypatch, settings, tmp_path):
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(segment_embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"

    segment_embeddings.upload_segment_embeddings({}, CapturingLog())

    assert captured["outbox_dir"] == tmp_path / "data" / "segment_embeddings_outbox"
    assert captured["archive_dir"] == tmp_path / "private" / "segment_embeddings_archive"
    assert captured["endpoint_path"] == "/api/pipeline/segment-embeddings/"
    assert captured["move_to_archive"] is True


def test_upload_segment_embeddings_archive_mode_reads_private_archive(monkeypatch, settings, tmp_path):
    captured = {}

    def fake_upload_jsonl_files_chunked(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(segment_embeddings, "upload_jsonl_files_chunked", fake_upload_jsonl_files_chunked)
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"

    segment_embeddings.upload_segment_embeddings({"archive": True}, CapturingLog())

    archive = tmp_path / "private" / "segment_embeddings_archive"
    assert captured["outbox_dir"] == archive
    assert captured["archive_dir"] == archive
    assert captured["move_to_archive"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest pipeline/tests/utils/upload/test_segment_embeddings.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# pipeline/utils/upload/segment_embeddings.py
from django.conf import settings

from pipeline.utils.http import upload_jsonl_files_chunked
from pipeline.log import Log


SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE = 100


def upload_segment_embeddings(options: dict, log: Log) -> None:
    archive_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive"
    upload_from_archive = options.get("archive", False)
    upload_jsonl_files_chunked(
        outbox_dir=archive_dir if upload_from_archive else settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox",
        archive_dir=archive_dir,
        endpoint_path="/api/pipeline/segment-embeddings/",
        chunk_size=SEGMENT_EMBEDDINGS_UPLOAD_CHUNK_SIZE,
        log=log,
        move_to_archive=not upload_from_archive,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest pipeline/tests/utils/upload/test_segment_embeddings.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Wire the command flag**

Modify `pipeline/management/commands/upload.py` — add to the mutually exclusive group:

```python
        group.add_argument("--segment_embeddings", action="store_true", help="Upload segment embedding JSONL from segment_embeddings_outbox/")
```

Add dispatch (after the `--embeddings` branch):

```python
        elif options["segment_embeddings"]:
            from pipeline.utils.upload.segment_embeddings import upload_segment_embeddings
            upload_segment_embeddings(options, log)
```

- [ ] **Step 6: Commit**

```bash
git add pipeline/utils/upload/segment_embeddings.py pipeline/tests/utils/upload/test_segment_embeddings.py pipeline/management/commands/upload.py
git commit -m "feat: add upload --segment_embeddings command"
```

---

### Task 7: `update --segment_embeddings` command

**Files:**
- Modify: `pipeline/management/commands/update.py`
- Test: `pipeline/tests/management/commands/test_update_segment_embeddings_command.py`

**Interfaces:**
- Consumes: `run_update_segment_embeddings` from `pipeline.utils.update.segment_embeddings` (Task 3, already implemented — this task only wires the CLI flag).

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/management/commands/test_update_segment_embeddings_command.py
import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_update_segment_embeddings_flag_dispatches(tmp_path, settings, monkeypatch):
    settings.PIPELINE_DATA_DIR = tmp_path
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path

    called = {}

    def fake_run(log, archive=False):
        called["archive"] = archive

    import pipeline.utils.update.segment_embeddings as module
    monkeypatch.setattr(module, "run_update_segment_embeddings", fake_run)
    monkeypatch.setattr(
        "pipeline.management.commands.update.Command.handle",
        __import__("pipeline.management.commands.update", fromlist=["Command"]).Command.handle,
    )

    call_command("update", segment_embeddings=True, archive=True)

    assert called == {"archive": True}
```

Note: the command imports `run_update_segment_embeddings` lazily inside `handle()`, so patching `pipeline.utils.update.segment_embeddings.run_update_segment_embeddings` before the command runs is sufficient — the awkward `monkeypatch.setattr(...Command.handle...)` line above is unnecessary; remove it. The corrected, simpler test:

```python
# pipeline/tests/management/commands/test_update_segment_embeddings_command.py
import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_update_segment_embeddings_flag_dispatches(monkeypatch):
    import pipeline.utils.update.segment_embeddings as module

    called = {}

    def fake_run(log, archive=False):
        called["archive"] = archive

    monkeypatch.setattr(module, "run_update_segment_embeddings", fake_run)

    call_command("update", segment_embeddings=True, archive=True)

    assert called == {"archive": True}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/management/commands/test_update_segment_embeddings_command.py -v`
Expected: FAIL with `CommandError: Error: one of the arguments --annotated --ep_meta --comedian_aliases --set_images --embeddings is required`

- [ ] **Step 3: Wire the command flag**

Modify `pipeline/management/commands/update.py`:

```python
        group.add_argument("--segment_embeddings", action="store_true", help="Write segment embeddings from segment_embeddings_inbox/ to DB")
```

```python
        elif options["segment_embeddings"]:
            from pipeline.utils.update.segment_embeddings import run_update_segment_embeddings
            run_update_segment_embeddings(log, archive=options["archive"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/management/commands/test_update_segment_embeddings_command.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pipeline/management/commands/update.py pipeline/tests/management/commands/test_update_segment_embeddings_command.py
git commit -m "feat: add update --segment_embeddings command"
```

---

### Task 8: Extract shared report JSON formatter (safe refactor, no behavior change)

**Files:**
- Create: `pipeline/utils/report_format.py`
- Modify: `pipeline/utils/generate/embeddings_report.py`
- Test: `pipeline/tests/utils/test_report_format.py`

**Interfaces:**
- Produces: `format_report_json(obj, level: int = 0) -> str`.

This is a pure move of the existing private `_fmt` function out of `embeddings_report.py` so the new segment report (Task 9) can reuse it without duplicating it. Behavior must be identical — the existing `test_generate_embedding_report.py` suite is the regression check.

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/utils/test_report_format.py
from pipeline.utils.report_format import format_report_json


def test_small_label_text_dict_stays_on_one_line():
    result = format_report_json({"label": "setup", "text": "hi"})
    assert result == '{"label": "setup", "text": "hi"}'


def test_list_of_strings_stays_on_one_line():
    result = format_report_json(["a", "b"])
    assert result == '["a", "b"]'


def test_nested_dict_is_multiline_and_indented():
    result = format_report_json({"pairs": [{"similarity": 1.0, "beat_a": {"id": 1}}]})
    assert result == (
        "{\n"
        '  "pairs": [\n'
        "    {\n"
        '      "similarity": 1.0,\n'
        '      "beat_a": {\n'
        '        "id": 1\n'
        "      }\n"
        "    }\n"
        "  ]\n"
        "}"
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/utils/test_report_format.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'pipeline.utils.report_format'`

- [ ] **Step 3: Extract the function**

```python
# pipeline/utils/report_format.py
import json


def format_report_json(obj, level: int = 0) -> str:
    """Pretty-print a report dict/list, keeping small {label, text} dicts and string lists on one line."""
    pad = "  " * level
    inner = "  " * (level + 1)
    if isinstance(obj, dict):
        if set(obj.keys()) <= {"label", "text"}:
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{json.dumps(k)}: {format_report_json(v, level + 1)}' for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if all(isinstance(x, str) for x in obj):
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{format_report_json(v, level + 1)}' for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)
```

In `pipeline/utils/generate/embeddings_report.py`:
- Remove the private `_fmt` function definition (lines 32-45 in the current file).
- Add `from pipeline.utils.report_format import format_report_json` to the imports.
- Replace both call sites — `output_path.write_text(_fmt(report), encoding="utf-8")` (appears twice, once in the "no new beats" early-return path and once at the end) — with `output_path.write_text(format_report_json(report), encoding="utf-8")`.

- [ ] **Step 4: Run tests to verify everything still passes**

Run: `pytest pipeline/tests/utils/test_report_format.py pipeline/tests/management/commands/test_generate_embedding_report.py -v`
Expected: PASS (existing embedding-report tests must be unaffected — this confirms the refactor preserved behavior)

- [ ] **Step 5: Commit**

```bash
git add pipeline/utils/report_format.py pipeline/utils/generate/embeddings_report.py pipeline/tests/utils/test_report_format.py
git commit -m "refactor: extract shared report JSON formatter"
```

---

### Task 9: `generate --segment_embeddings_report` command

**Files:**
- Create: `pipeline/utils/generate/segment_embeddings_report.py`
- Modify: `pipeline/management/commands/generate.py`
- Test: `pipeline/tests/management/commands/test_generate_segment_embedding_report.py`

**Interfaces:**
- Consumes: `format_report_json` from `pipeline.utils.report_format` (Task 8); `BeatSegment` from `pipeline.models` (Task 2).
- Produces: `generate_segment_embeddings_report(log: Log) -> None`. Writes `segment_embedding_similarity_report.json` to `settings.PIPELINE_PRIVATE_DATA_DIR`.

- [ ] **Step 1: Write the failing tests**

```python
# pipeline/tests/management/commands/test_generate_segment_embedding_report.py
import json

import pytest
from django.core.management import call_command
from django.test import override_settings

from pipeline.models import Beat, BeatSegment, Bit, Comedian, Line, Set, Video

pytestmark = pytest.mark.django_db


def _make_set(name, slug, set_number):
    comedian = Comedian.objects.create(name=name, slug=slug)
    video = Video.objects.create(video_id=f"vid-{slug}", title=f"Episode {slug}", url=f"https://example.com/{slug}")
    return Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=float(set_number * 10))


def _make_beat(standup_set, beat_id, premise, joke_type="misdirect"):
    bit = Bit.objects.create(set=standup_set, bit_id=f"bit-{beat_id}", line_start=1, line_end=1)
    return Beat.objects.create(bit=bit, beat_id=beat_id, line_start=1, line_end=1, premise=premise, joke_type=joke_type)


def test_report_matches_segments_across_different_comedians(tmp_path):
    set_a = _make_set("Comic One", "comic-one", 1)
    set_b = _make_set("Comic Two", "comic-two", 1)
    beat_a = _make_beat(set_a, "a", "premise a")
    beat_b = _make_beat(set_b, "b", "premise b")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="the punchline text", line_start=1, line_end=1, embedding=[1.0, 0.0])
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="the punchline text", line_start=1, line_end=1, embedding=[1.0, 0.0])

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert payload["threshold"] == 0.70
    assert len(payload["pairs"]) == 1
    pair = payload["pairs"][0]
    assert pair["similarity"] == 1.0
    assert {pair["beat_a"]["id"], pair["beat_b"]["id"]} == {beat_a.id, beat_b.id}
    assert pair["beat_a"]["matched_segment"]["text"] == "the punchline text"


def test_report_does_not_match_segments_from_same_comedian(tmp_path):
    set_a = _make_set("Comic One", "comic-one-2", 1)
    beat_a = _make_beat(set_a, "a", "premise a")
    beat_b = _make_beat(set_a, "b", "premise b")
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="text", line_start=1, line_end=1, embedding=[1.0, 0.0])
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="text", line_start=1, line_end=1, embedding=[1.0, 0.0])

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert payload["pairs"] == []


def test_report_takes_best_segment_pair_per_beat_pair(tmp_path):
    set_a = _make_set("Comic One", "comic-one-3", 1)
    set_b = _make_set("Comic Two", "comic-two-3", 1)
    beat_a = _make_beat(set_a, "a", "premise a")
    beat_b = _make_beat(set_b, "b", "premise b")
    # Two segments per beat; only one pair (seg 2 x seg 2) is a strong match.
    BeatSegment.objects.create(beat=beat_a, ordinal=1, text="unrelated setup", line_start=1, line_end=1, embedding=[0.0, 1.0])
    BeatSegment.objects.create(beat=beat_a, ordinal=2, text="matching punchline", line_start=2, line_end=2, embedding=[1.0, 0.0])
    BeatSegment.objects.create(beat=beat_b, ordinal=1, text="different setup", line_start=1, line_end=1, embedding=[0.0, -1.0])
    BeatSegment.objects.create(beat=beat_b, ordinal=2, text="matching punchline", line_start=2, line_end=2, embedding=[1.0, 0.0])

    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    payload = json.loads((tmp_path / "segment_embedding_similarity_report.json").read_text(encoding="utf-8"))
    assert len(payload["pairs"]) == 1
    assert payload["pairs"][0]["similarity"] == 1.0
    assert payload["pairs"][0]["beat_a"]["matched_segment"]["text"] == "matching punchline"


def test_report_warns_when_no_embedded_segments_exist(tmp_path):
    with override_settings(PIPELINE_PRIVATE_DATA_DIR=tmp_path):
        call_command("generate", segment_embeddings_report=True)

    assert not (tmp_path / "segment_embedding_similarity_report.json").exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest pipeline/tests/management/commands/test_generate_segment_embedding_report.py -v`
Expected: FAIL with `CommandError: Error: one of the arguments ... is required` (flag not wired yet)

- [ ] **Step 3: Implement the report generator**

```python
# pipeline/utils/generate/segment_embeddings_report.py
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from django.conf import settings
from django.utils import timezone

from pipeline.log import Log
from pipeline.models import BeatSegment
from pipeline.utils.report_format import format_report_json

OUTPUT_FILENAME = "segment_embedding_similarity_report.json"
DEFAULT_THRESHOLD = 0.70


@dataclass(frozen=True)
class SegmentRecord:
    id: int
    beat_id: int
    joke_type: str | None
    premise: str | None
    text: str
    line_start: int
    line_end: int
    comedian_id: int
    comedian_name: str
    vector: np.ndarray


def _cosine_sim(a, b):
    return float(np.dot(a, b))


def _normalized_vector(embedding):
    vector = np.asarray(embedding, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def _build_segment_records(qs) -> list[SegmentRecord]:
    records = []
    for segment in qs:
        beat = segment.beat
        records.append(SegmentRecord(
            id=segment.id,
            beat_id=beat.id,
            joke_type=beat.joke_type,
            premise=beat.premise,
            text=segment.text,
            line_start=segment.line_start,
            line_end=segment.line_end,
            comedian_id=beat.bit.set.comedian_id,
            comedian_name=beat.bit.set.comedian.name,
            vector=_normalized_vector(segment.embedding),
        ))
    return records


def generate_segment_embeddings_report(log: Log) -> None:
    threshold = DEFAULT_THRESHOLD
    output_path = settings.PIPELINE_PRIVATE_DATA_DIR / OUTPUT_FILENAME

    qs = BeatSegment.objects.exclude(embedding=[]).select_related("beat__bit__set__comedian")
    segments = _build_segment_records(qs)
    log(f"Loaded {len(segments)} beat segments with embeddings.")
    if not segments:
        log.warning(
            "No segment embeddings are stored in this database. "
            "Run `python manage.py generate --segment_embeddings` and ingest them before generating a report."
        )
        return

    groups: dict[str, list[SegmentRecord]] = {}
    for segment in segments:
        groups.setdefault(segment.joke_type or "unknown", []).append(segment)

    best_by_beat_pair: dict[tuple[int, int], dict] = {}
    for label, group in groups.items():
        n_pairs = len(group) * (len(group) - 1) // 2
        if n_pairs == 0:
            continue
        log(f"\n  {label}: {len(group)} segments, {n_pairs:,} segment pairs")
        for a, b in combinations(group, 2):
            if a.comedian_id == b.comedian_id:
                continue
            sim = round(_cosine_sim(a.vector, b.vector), 4)
            if sim < threshold:
                continue
            beat_pair_key = tuple(sorted((a.beat_id, b.beat_id)))
            existing = best_by_beat_pair.get(beat_pair_key)
            if existing is None or sim > existing["similarity"]:
                best_by_beat_pair[beat_pair_key] = {"similarity": sim, "a": a, "b": b}

    pairs = []
    for match in best_by_beat_pair.values():
        a, b = match["a"], match["b"]
        pairs.append({
            "similarity": match["similarity"],
            "beat_a": {
                "id": a.beat_id, "joke_type": a.joke_type, "comedian": a.comedian_name, "premise": a.premise,
                "matched_segment": {"text": a.text, "line_start": a.line_start, "line_end": a.line_end},
            },
            "beat_b": {
                "id": b.beat_id, "joke_type": b.joke_type, "comedian": b.comedian_name, "premise": b.premise,
                "matched_segment": {"text": b.text, "line_start": b.line_start, "line_end": b.line_end},
            },
        })
    pairs.sort(key=lambda p: p["similarity"], reverse=True)

    report = {"generated_at": timezone.now().isoformat(), "threshold": threshold, "pairs": pairs}
    output_path.write_text(format_report_json(report), encoding="utf-8")

    log.success(
        f"\nFound {len(pairs)} beat pair(s) with a matching segment above threshold {threshold}. "
        f"Written to {output_path}"
    )
```

- [ ] **Step 4: Wire the command flag**

Modify `pipeline/management/commands/generate.py` — add to the mutually exclusive group (after `--embeddings_report`):

```python
        group.add_argument("--segment_embeddings_report", action="store_true", help="Generate joke similarity report from stored segment embeddings")
```

Add dispatch (after the `--embeddings_report` branch):

```python
        elif options["segment_embeddings_report"]:
            from pipeline.utils.generate.segment_embeddings_report import generate_segment_embeddings_report
            generate_segment_embeddings_report(log)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest pipeline/tests/management/commands/test_generate_segment_embedding_report.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
git add pipeline/utils/generate/segment_embeddings_report.py pipeline/tests/management/commands/test_generate_segment_embedding_report.py pipeline/management/commands/generate.py
git commit -m "feat: add generate --segment_embeddings_report command"
```

---

### Task 10: Wire up `reset_db`, `.gitignore`, and docs

**Files:**
- Modify: `pipeline/management/commands/reset_db.py`
- Modify: `pipeline/data_private/.gitignore`
- Modify: `docs/pipeline.md`
- Test: `pipeline/tests/management/commands/test_reset_db_segment_embeddings.py`

**Interfaces:**
- Consumes: `run_update_segment_embeddings` via `call_command("update", segment_embeddings=True, archive=True)` (Task 7).

- [ ] **Step 1: Write the failing test**

```python
# pipeline/tests/management/commands/test_reset_db_segment_embeddings.py
import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def test_reset_db_restores_segment_embeddings_from_archive(tmp_path, settings, monkeypatch):
    archive_dir = tmp_path / "private" / "segment_embeddings_archive"
    archive_dir.mkdir(parents=True)
    (archive_dir / "segment_embeddings.jsonl").write_text('{"key": "x", "embedding": [1.0]}\n', encoding="utf-8")

    settings.BASE_DIR = tmp_path
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"
    (settings.PIPELINE_DATA_DIR).mkdir(parents=True, exist_ok=True)
    (tmp_path / "pipeline" / "migrations").mkdir(parents=True, exist_ok=True)
    (tmp_path / "mediafiles").mkdir(parents=True, exist_ok=True)
    settings.MEDIA_ROOT = tmp_path / "mediafiles"

    calls = []
    monkeypatch.setattr(
        "pipeline.management.commands.reset_db.call_command",
        lambda name, **kwargs: calls.append((name, kwargs)),
    )
    monkeypatch.setattr("pipeline.management.commands.reset_db.connection", type("C", (), {
        "cursor": lambda self: __import__("contextlib").nullcontext(type("Cur", (), {
            "execute": lambda self, sql: None,
        })()),
        "introspection": type("I", (), {"table_names": lambda self, cursor: []})(),
    })())

    call_command("reset_db")

    assert ("update", {"segment_embeddings": True, "archive": True}) in calls
```

This test is heavier than the others because `reset_db` does real schema/table operations — it's here to confirm the *dispatch* (that `update --segment_embeddings --archive` gets called when the archive dir is populated), not to re-test `reset_db`'s existing DB-wiping behavior. If mocking `connection` this way proves too brittle when actually run, replace it with a real (empty) test database and let the existing DB operations run for real — `reset_db` is already exercised in some form elsewhere in the suite; check for an existing `test_reset_db*.py` first and follow whatever pattern it already uses instead of inventing a new mocking approach.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest pipeline/tests/management/commands/test_reset_db_segment_embeddings.py -v`
Expected: FAIL (the `("update", {"segment_embeddings": True, "archive": True})` call is never made)

- [ ] **Step 3: Wire reset_db**

In `pipeline/management/commands/reset_db.py`, after the existing block:

```python
        embeddings_archive = private_dir / "embeddings_archive"
        if embeddings_archive.exists() and any(embeddings_archive.glob("*.jsonl")):
            self.stdout.write("\nRestoring embeddings from archive...")
            call_command("update", embeddings=True, archive=True)
        else:
            self.stdout.write("\nNo archived embeddings to restore.")
```

add:

```python
        segment_embeddings_archive = private_dir / "segment_embeddings_archive"
        if segment_embeddings_archive.exists() and any(segment_embeddings_archive.glob("*.jsonl")):
            self.stdout.write("\nRestoring segment embeddings from archive...")
            call_command("update", segment_embeddings=True, archive=True)
        else:
            self.stdout.write("\nNo archived segment embeddings to restore.")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest pipeline/tests/management/commands/test_reset_db_segment_embeddings.py -v`
Expected: PASS

- [ ] **Step 5: Update `.gitignore` to track the new archive and report**

In `pipeline/data_private/.gitignore`, add after the existing `!embedding_similarity_report.json` line:

```
!segment_embeddings_archive/
!segment_embeddings_archive/**
!segment_embedding_similarity_report.json
```

- [ ] **Step 6: Update `docs/pipeline.md`**

Add rows to the data directories table (after the `embedding_similarity_report.json` row):

```
| `segment_embeddings_outbox/` | Computed segment embeddings JSONL awaiting upload |
| `segment_embeddings_inbox/` | (server) Received JSONL awaiting `update --segment_embeddings` |
| `segment_embeddings_archive/` | Archived segment embedding vectors (private git) |
| `segment_embedding_similarity_report.json` | Segment-level joke similarity report — experimental parallel to `embedding_similarity_report.json` (private git) |
```

Add a new section after "5. Joke similarity scoring":

```markdown
**6. Segment-based joke similarity scoring (experimental):**
```
python manage.py generate --segment_embeddings
python manage.py upload --segment_embeddings
python manage.py update --segment_embeddings
python manage.py generate --segment_embeddings_report
```
Purpose: parallel to step 5, but embeds beats at the level of packed sentence-groups ("segments") instead of one vector per whole beat, so a reused punchline surrounded by a different setup can still surface as a match. Segments are built once per beat (ignoring `setup`/`punchline`/`tag`/`fluff` labels entirely — every line in the beat's range is used) the first time that beat is requested for embedding, and persisted to the `BeatSegment` table. Uses the same embedding model as step 5 so the two reports (`embedding_similarity_report.json` vs `segment_embedding_similarity_report.json`) are comparable on everything except text granularity.
```

Renumber the old "6. Optional maintenance/reset" section to "7."

- [ ] **Step 7: Commit**

```bash
git add pipeline/management/commands/reset_db.py pipeline/data_private/.gitignore docs/pipeline.md pipeline/tests/management/commands/test_reset_db_segment_embeddings.py
git commit -m "feat: wire segment embeddings into reset_db, gitignore, and docs"
```

---

## Self-Review

**Spec coverage:**
- Segment beats by packed sentences (min-word floor, no max, close-on-reaching-floor, no-accretion-into-closed-segments, trailing-leftover-merges-backward) → Task 1.
- Ignore line labels entirely, pull raw beat text → Task 1 (`segment_beat_lines` takes unlabeled `(line_number, text)` tuples) + Task 3 (`_load_all_lines_by_set` has no label filter).
- Persist segments with provenance (`line_start`/`line_end`) for evidence → Task 2 + Task 9 (`matched_segment` in report output).
- Same embedding model as existing pipeline, for a clean comparison → Task 5 (hardcoded `"all-mpnet-base-v2"`, same as `generate_embeddings.py`).
- Full generate/upload/update round trip mirroring the existing pipeline → Tasks 4-7.
- A new, separate report file so it can be compared against the existing one → Task 9 (`segment_embedding_similarity_report.json`, separate constant, separate function, best-segment-pair-per-beat-pair aggregation with matching-span evidence).
- Existing pipeline untouched except one explicitly-scoped, behavior-preserving refactor → Task 8, verified against existing tests.
- Dev-reset and doc parity with the existing pipeline → Task 10.

**Placeholder scan:** No "TBD"/"handle edge cases"/"similar to Task N" phrasing present; every code step has complete, runnable code. Task 10's Step 1 test includes an explicit caveat pointing the implementer at an existing `test_reset_db*.py` pattern if the given mocking approach proves brittle — this is a legitimate implementation judgment call (which mocking style fits the existing `reset_db` test suite), not a missing spec, since no `reset_db` test file existed to mirror at planning time.

**Type/signature consistency:** `Segment` (Task 1) is consumed as `.text`/`.line_start`/`.line_end` in Task 3's `ensure_beat_segments` — matches. `BeatSegment.embedding` (Task 2, default `[]`) matches the `exclude(embedding=[])` / `filter(embedding=[])` queries in Tasks 3 and 9. `unembedded_beat_segments()` return shape (`{"key", "text"}`) matches what Task 5's `generate_segment_embeddings` consumes (`s["key"]`, `s["text"]`). Key format `ep{n}.set{n:02d}.bit{n:03d}.beat{n:03d}.seg{n:03d}` is produced identically in Task 3 (`unembedded_beat_segments`) and parsed identically in Task 3 (`_parse_segment_key`) and referenced identically in the Task 4 test's assertion (`.seg001`) and Task 3 test fixtures. `format_report_json` (Task 8) is imported by name identically in Task 9.

---

**Plan complete and saved to `docs/superpowers/plans/2026-07-05-segment-embedding-report.md`.** Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**

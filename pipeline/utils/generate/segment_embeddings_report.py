import time

import numpy as np
from django.conf import settings
from django.utils import timezone

from pipeline.log import Log
from pipeline.models import BeatSegment
from pipeline.utils.report_format import format_report_json
from pipeline.utils.vectors import EMPTY_EMBEDDING, unpack_matrix


OUTPUT_FILENAME = "segment_embedding_similarity_report.json"
DEFAULT_THRESHOLD = 0.70
COMPARE_BLOCK_SIZE = 512
LOAD_CHUNK_SIZE = 2000


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes}m{seconds:02d}s"


def _progress(done: int, total: int, started: float) -> str:
    elapsed = time.monotonic() - started
    rate = done / elapsed if elapsed > 0 else 0
    remaining = (total - done) / rate if rate > 0 else 0
    return (
        f"{done:,}/{total:,} ({100 * done / total:.1f}%) | "
        f"elapsed {_format_duration(elapsed)} | eta {_format_duration(remaining)}"
    )


def _load_segments(log: Log):
    """Load every embedded segment as parallel numpy arrays.

    Deliberately avoids model instantiation: at ~20k segments a select_related
    queryset builds ~100k throwaway objects to read four fields off each. Text and
    comedian names are fetched later, only for the segments that win a beat pair.

    Fetched in id-ordered chunks rather than one query so the load can report
    progress, and so peak memory stays proportional to a chunk rather than to the
    whole table.
    """
    base = BeatSegment.objects.exclude(embedding=EMPTY_EMBEDDING)
    total = base.count()
    if total == 0:
        return None

    log(f"Loading {total:,} embedded segments from the database...")
    started = time.monotonic()

    segment_ids: list[int] = []
    beat_ids: list[int] = []
    comedian_ids: list[int] = []
    blocks: list[np.ndarray] = []
    after_id = 0

    while True:
        rows = list(
            base
            .filter(id__gt=after_id)
            .order_by("id")
            .values_list("id", "beat_id", "beat__bit__set__comedian_id", "embedding")[:LOAD_CHUNK_SIZE]
        )
        if not rows:
            break

        segment_ids.extend(row[0] for row in rows)
        beat_ids.extend(row[1] for row in rows)
        comedian_ids.extend(row[2] for row in rows)
        blocks.append(unpack_matrix(row[3] for row in rows))
        after_id = rows[-1][0]

        log(f"  {_progress(len(segment_ids), total, started)}")

    log(f"  Loaded in {_format_duration(time.monotonic() - started)}. Normalizing vectors...")
    matrix = np.vstack(blocks)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    matrix /= norms

    return (
        np.asarray(segment_ids, dtype=np.int64),
        np.asarray(beat_ids, dtype=np.int64),
        np.asarray(comedian_ids, dtype=np.int64),
        matrix,
    )


def _find_matches(matrix, comedian_ids, threshold: float, log: Log):
    """Every cross-comedian segment pair scoring at or above `threshold`.

    Compares all segments against each other regardless of joke type. Each block is
    multiplied only against the columns at or after it, so the lower triangle is
    never computed.
    """
    n = len(matrix)
    total_pairs = n * (n - 1) // 2
    empty = (np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float32))
    if total_pairs == 0:
        return empty

    log(f"\nComparing {n:,} segments ({total_pairs:,} segment pairs) at threshold {threshold}...")
    started = time.monotonic()

    left, right, scores = [], [], []
    found = 0
    for start in range(0, n, COMPARE_BLOCK_SIZE):
        end = min(start + COMPARE_BLOCK_SIZE, n)
        similarities = matrix[start:end] @ matrix[start:].T

        row_indices = np.arange(start, end)[:, None]
        col_indices = np.arange(start, n)[None, :]
        upper_triangle = col_indices > row_indices
        cross_comedian = comedian_ids[start:end, None] != comedian_ids[None, start:]

        hit_rows, hit_cols = np.where(upper_triangle & cross_comedian & (similarities >= threshold))
        if hit_rows.size:
            left.append(start + hit_rows)
            right.append(start + hit_cols)
            scores.append(similarities[hit_rows, hit_cols])
            found += hit_rows.size

        remaining = (n - end) * (n - end - 1) // 2
        log(f"  {_progress(total_pairs - remaining, total_pairs, started)} | {found:,} matching segment pair(s)")

    log(f"  Compared in {_format_duration(time.monotonic() - started)}.")
    if not left:
        return empty
    return np.concatenate(left), np.concatenate(right), np.concatenate(scores)


def _best_per_beat_pair(left, right, scores, beat_ids) -> dict[tuple[int, int], tuple[float, int, int]]:
    """Collapse segment pairs to one row per beat pair: the highest-scoring segment pair.

    Returns beat_pair -> (similarity, segment index for beat_a, segment index for beat_b).
    """
    best: dict[tuple[int, int], tuple[float, int, int]] = {}
    for i, j, score in zip(left, right, scores):
        beat_a, beat_b = int(beat_ids[i]), int(beat_ids[j])
        if beat_a > beat_b:
            beat_a, beat_b, i, j = beat_b, beat_a, j, i
        key = (beat_a, beat_b)
        score = round(float(score), 4)
        existing = best.get(key)
        if existing is None or score > existing[0]:
            best[key] = (score, int(i), int(j))
    return best


def _segment_details(segment_ids, needed_indices) -> dict[int, tuple[str, str]]:
    """Fetch text and comedian name for just the segments that appear in the report."""
    wanted = [int(segment_ids[index]) for index in needed_indices]
    rows = (
        BeatSegment.objects
        .filter(id__in=wanted)
        .values_list("id", "text", "beat__bit__set__comedian__name")
    )
    return {row[0]: (row[1], row[2]) for row in rows}


def generate_segment_embeddings_report(log: Log) -> None:
    threshold = DEFAULT_THRESHOLD
    output_path = settings.PIPELINE_PRIVATE_DATA_DIR / OUTPUT_FILENAME
    started = time.monotonic()

    loaded = _load_segments(log)
    if loaded is None:
        log.warning(
            "No segment embeddings are stored in this database. "
            "Run `python manage.py generate --segment_embeddings` and ingest them before generating a report."
        )
        return

    segment_ids, beat_ids, comedian_ids, matrix = loaded

    left, right, scores = _find_matches(matrix, comedian_ids, threshold, log)
    best = _best_per_beat_pair(left, right, scores, beat_ids)
    log(f"\nReduced {len(scores):,} segment pair(s) to {len(best):,} beat pair(s).")

    ordered = sorted(best.items(), key=lambda item: (-item[1][0], item[0]))
    needed = [index for _, (_, i, j) in ordered for index in (i, j)]
    log(f"Fetching text and comedian names for {len(needed):,} matched segment(s)...")
    details = _segment_details(segment_ids, needed)

    pairs = []
    for _, (similarity, index_a, index_b) in ordered:
        text_a, comedian_a = details[int(segment_ids[index_a])]
        text_b, comedian_b = details[int(segment_ids[index_b])]
        pairs.append({
            "similarity": similarity,
            "beat_a": {"comedian": comedian_a, "matched_segment": text_a},
            "beat_b": {"comedian": comedian_b, "matched_segment": text_b},
        })

    log(f"Writing {output_path.name}...")
    report = {"generated_at": timezone.now().isoformat(), "threshold": threshold, "pairs": pairs}
    output_path.write_text(format_report_json(report), encoding="utf-8")

    log.success(
        f"\nFound {len(pairs)} beat pair(s) with a matching segment above threshold {threshold} "
        f"in {_format_duration(time.monotonic() - started)}. Written to {output_path}"
    )

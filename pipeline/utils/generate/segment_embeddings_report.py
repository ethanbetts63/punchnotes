from dataclasses import dataclass

import numpy as np
from django.conf import settings
from django.utils import timezone

from pipeline.log import Log
from pipeline.models import BeatSegment
from pipeline.utils.report_format import format_report_json


OUTPUT_FILENAME = "segment_embedding_similarity_report.json"
DEFAULT_THRESHOLD = 0.70
COMPARE_BLOCK_SIZE = 512


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


def _update_best_match(best_by_beat_pair: dict[tuple[int, int], dict], sim: float, a: SegmentRecord, b: SegmentRecord) -> bool:
    beat_pair_key = tuple(sorted((a.beat_id, b.beat_id)))
    existing = best_by_beat_pair.get(beat_pair_key)
    if existing is None or sim > existing["similarity"]:
        best_by_beat_pair[beat_pair_key] = {"similarity": sim, "a": a, "b": b}
        return existing is None
    return False


def _compare_group(label: str, group: list[SegmentRecord], threshold: float, best_by_beat_pair: dict[tuple[int, int], dict], log: Log) -> None:
    n_pairs = len(group) * (len(group) - 1) // 2
    if n_pairs == 0:
        return

    log(f"\n  {label}: {len(group)} segments, {n_pairs:,} segment pairs")

    vectors = np.vstack([record.vector for record in group]).astype(np.float32, copy=False)
    comedian_ids = np.asarray([record.comedian_id for record in group])

    checked_pairs = 0
    same_comedian_skipped = 0
    retained_matches = 0

    all_indices = np.arange(len(group))
    for block_start in range(0, len(group), COMPARE_BLOCK_SIZE):
        block_end = min(block_start + COMPARE_BLOCK_SIZE, len(group))
        block = vectors[block_start:block_end]
        similarities = block @ vectors.T

        row_indices = np.arange(block_start, block_end)[:, None]
        upper_triangle_mask = all_indices[None, :] > row_indices
        cross_comedian_mask = comedian_ids[block_start:block_end, None] != comedian_ids[None, :]
        candidate_mask = upper_triangle_mask & cross_comedian_mask

        checked_pairs += int(upper_triangle_mask.sum())
        same_comedian_skipped += int((upper_triangle_mask & ~cross_comedian_mask).sum())

        match_rows, match_cols = np.where(candidate_mask & (similarities >= threshold))
        for local_row, col in zip(match_rows, match_cols):
            sim = round(float(similarities[local_row, col]), 4)
            if _update_best_match(best_by_beat_pair, sim, group[block_start + local_row], group[col]):
                retained_matches += 1

        percent = 100 * checked_pairs / n_pairs
        log(
            f"    {checked_pairs:,}/{n_pairs:,} ({percent:.1f}%) | "
            f"{retained_matches} retained matches | "
            f"{same_comedian_skipped:,} same-comedian skipped"
        )

    log(f"  Done: {retained_matches} retained beat-pair match(es)")


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
        _compare_group(label, group, threshold, best_by_beat_pair, log)

    pairs = []
    for match in best_by_beat_pair.values():
        a, b = match["a"], match["b"]
        pairs.append({
            "similarity": match["similarity"],
            "beat_a": {
                "id": a.beat_id,
                "joke_type": a.joke_type,
                "comedian": a.comedian_name,
                "premise": a.premise,
                "matched_segment": {"text": a.text, "line_start": a.line_start, "line_end": a.line_end},
            },
            "beat_b": {
                "id": b.beat_id,
                "joke_type": b.joke_type,
                "comedian": b.comedian_name,
                "premise": b.premise,
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

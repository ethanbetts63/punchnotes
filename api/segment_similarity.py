import time

import numpy as np
from django.db.models import Count, Max

from pipeline.models import BeatSegment
from pipeline.utils.vectors import EMPTY_EMBEDDING, unpack_matrix

DEFAULT_THRESHOLD = 0.70
DEFAULT_TOP_N = 10

# How long a cached corpus may serve before being reloaded. The fingerprint below
# catches added/removed segment rows cheaply, but embedding ingest bulk-updates
# EXISTING rows, which (count, max id) cannot see -- the TTL bounds that staleness.
CORPUS_MAX_AGE_SECONDS = 600

_corpus = {"fingerprint": None, "loaded_at": 0.0, "segment_ids": None, "beat_ids": None, "matrix": None}


def _fingerprint():
    agg = BeatSegment.objects.aggregate(n=Count("id"), latest=Max("id"))
    return (agg["n"], agg["latest"])


def _corpus_arrays():
    """The full corpus as (segment_ids, beat_ids, normalized matrix), cached in process memory.

    Loading ~63 MB of vectors from the database is the dominant cost of a similarity
    check, and the corpus only changes when the pipeline ingests new embeddings, so
    it is loaded once per process and revalidated with one indexed aggregate query.
    """
    now = time.monotonic()
    fingerprint = _fingerprint()
    if (
        _corpus["matrix"] is not None
        and _corpus["fingerprint"] == fingerprint
        and now - _corpus["loaded_at"] < CORPUS_MAX_AGE_SECONDS
    ):
        return _corpus["segment_ids"], _corpus["beat_ids"], _corpus["matrix"]

    rows = list(
        BeatSegment.objects
        .exclude(embedding=EMPTY_EMBEDDING)
        .order_by("id")
        .values_list("id", "beat_id", "embedding")
    )
    if rows:
        segment_ids = np.asarray([row[0] for row in rows], dtype=np.int64)
        beat_ids = np.asarray([row[1] for row in rows], dtype=np.int64)
        matrix = unpack_matrix(row[2] for row in rows)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0  # zero vectors stay zero and can never clear the threshold
        matrix /= norms
    else:
        segment_ids = beat_ids = matrix = None

    _corpus.update(fingerprint=fingerprint, loaded_at=now, segment_ids=segment_ids, beat_ids=beat_ids, matrix=matrix)
    return segment_ids, beat_ids, matrix


def find_similar_beats_by_segments(
    query_vectors: list[np.ndarray],
    top_n: int = DEFAULT_TOP_N,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict]:
    """Match query segment vectors against every stored beat segment.

    Each stored segment is scored by its best (max) similarity across the query
    segments. Segments above ``threshold`` are grouped by beat; beats are ranked
    by their single best matching segment. Returns, per beat, the beat plus its
    matched segments (each with its own score), so callers can highlight exactly
    which lines matched.
    """
    if not query_vectors:
        return []

    segment_ids, beat_ids, matrix = _corpus_arrays()
    if matrix is None:
        return []

    query = np.vstack([np.asarray(q, dtype=np.float32) for q in query_vectors])
    similarities = query @ matrix.T
    best_per_segment = similarities.max(axis=0)

    hits = np.where(best_per_segment >= threshold)[0]
    if hits.size == 0:
        return []

    # Only the matching segments are hydrated from the database. Set lines are not
    # prefetched either: callers render lines for the few beats returned, and those
    # lazy-load per winning set.
    matched = (
        BeatSegment.objects
        .filter(id__in=[int(segment_ids[i]) for i in hits])
        .select_related("beat__bit__set__comedian", "beat__bit__set__video")
    )
    segments_by_id = {segment.id: segment for segment in matched}

    by_beat: dict[int, dict] = {}
    for index in hits:
        segment = segments_by_id.get(int(segment_ids[index]))
        if segment is None:  # deleted since the corpus was cached
            continue
        score = float(best_per_segment[index])
        entry = by_beat.setdefault(int(beat_ids[index]), {"beat": segment.beat, "segments": [], "best": 0.0})
        entry["segments"].append((segment, score))
        if score > entry["best"]:
            entry["best"] = score

    ranked = sorted(by_beat.values(), key=lambda entry: entry["best"], reverse=True)[:top_n]
    for entry in ranked:
        entry["segments"].sort(key=lambda pair: pair[1], reverse=True)
    return ranked

import numpy as np

from pipeline.models import BeatSegment

DEFAULT_THRESHOLD = 0.70
DEFAULT_TOP_N = 10


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

    segments = (
        BeatSegment.objects
        .exclude(embedding=[])
        .select_related("beat__bit__set__comedian", "beat__bit__set__video")
        .prefetch_related("beat__bit__set__lines")
    )

    seg_list = []
    vectors = []
    for segment in segments:
        vector = np.asarray(segment.embedding, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            continue
        vectors.append(vector / norm)
        seg_list.append(segment)

    if not seg_list:
        return []

    corpus = np.vstack(vectors).astype(np.float32, copy=False)
    query = np.vstack([np.asarray(q, dtype=np.float32) for q in query_vectors])
    similarities = query @ corpus.T
    best_per_segment = similarities.max(axis=0)

    by_beat: dict[int, dict] = {}
    for index, score in enumerate(best_per_segment):
        score = float(score)
        if score < threshold:
            continue
        segment = seg_list[index]
        beat = segment.beat
        entry = by_beat.setdefault(beat.id, {"beat": beat, "segments": [], "best": 0.0})
        entry["segments"].append((segment, score))
        if score > entry["best"]:
            entry["best"] = score

    ranked = sorted(by_beat.values(), key=lambda entry: entry["best"], reverse=True)[:top_n]
    for entry in ranked:
        entry["segments"].sort(key=lambda pair: pair[1], reverse=True)
    return ranked

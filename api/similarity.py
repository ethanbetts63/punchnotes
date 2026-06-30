import numpy as np

from pipeline.models import Beat

DEFAULT_THRESHOLD = 0.70
DEFAULT_TOP_N = 10


def find_similar_beats(query_vector: np.ndarray, top_n: int = DEFAULT_TOP_N, threshold: float = DEFAULT_THRESHOLD):
    beats = (
        Beat.objects
        .exclude(embedding=[])
        .select_related("bit__set__comedian", "bit__set__video")
        .prefetch_related("bit__set__lines")
    )

    results = []
    for beat in beats:
        vector = np.array(beat.embedding, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm == 0:
            continue
        vector = vector / norm
        sim = float(np.dot(query_vector, vector))
        if sim >= threshold:
            results.append((sim, beat))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_n]

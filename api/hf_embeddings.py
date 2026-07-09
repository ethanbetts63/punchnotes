from hashlib import sha256
import time

import numpy as np
import requests
from django.core.cache import cache
from django.conf import settings

_HF_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-mpnet-base-v2/pipeline/feature-extraction"
_MAX_WAIT_SECONDS = 120
_EMBEDDING_CACHE_TIMEOUT = 60 * 60 * 24 * 7


def embedding_cache_key(text: str) -> str:
    return f"embed:{sha256(text.encode('utf-8')).hexdigest()}"


def embed_texts(texts: list[str]) -> list[np.ndarray]:
    """Embed texts, making one HTTP request for every cache miss combined.

    A long paste segments into ~25 texts; sending them as a single batch avoids
    that many sequential round trips to the inference API.
    """
    vectors: dict[int, np.ndarray] = {}
    missing: list[int] = []
    for index, text in enumerate(texts):
        cached = cache.get(embedding_cache_key(text))
        if cached is not None:
            vectors[index] = cached
        else:
            missing.append(index)

    if missing:
        rows = _request_embeddings([texts[index] for index in missing])
        for index, row in zip(missing, rows):
            vector = _normalized(row)
            cache.set(embedding_cache_key(texts[index]), vector, timeout=_EMBEDDING_CACHE_TIMEOUT)
            vectors[index] = vector

    return [vectors[index] for index in range(len(texts))]


def embed_text(text: str) -> np.ndarray:
    return embed_texts([text])[0]


def _request_embeddings(texts: list[str]) -> list:
    """POST one batch to the feature-extraction endpoint, waiting out model cold starts."""
    headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
    payload = {"inputs": texts, "options": {"wait_for_model": True}}

    deadline = time.time() + _MAX_WAIT_SECONDS
    while True:
        resp = requests.post(_HF_URL, headers=headers, json=payload, timeout=_MAX_WAIT_SECONDS)

        if resp.status_code == 503:
            data = resp.json()
            wait = float(data.get("estimated_time") or 20)
            remaining = deadline - time.time()
            if remaining <= 0:
                raise TimeoutError("HuggingFace model did not become ready in time.")
            time.sleep(min(wait, remaining) + 1)
            continue

        resp.raise_for_status()

        rows = resp.json()
        if len(rows) != len(texts):
            raise ValueError(f"Expected {len(texts)} embeddings from HuggingFace, got {len(rows)}.")
        return rows


def _normalized(row) -> np.ndarray:
    vector = np.asarray(row, dtype=np.float32)
    # Guard against token-level output shape [tokens x dims]; the pooled vector is row 0.
    if vector.ndim > 1:
        vector = vector[0]
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector

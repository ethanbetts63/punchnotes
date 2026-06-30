import time

import numpy as np
import requests
from django.core.cache import cache
from django.conf import settings

_HF_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-mpnet-base-v2/pipeline/feature-extraction"
_MAX_WAIT_SECONDS = 120


def embed_text(text: str) -> np.ndarray:
    cached = cache.get(f"embed:{text}")
    if cached is not None:
        return cached

    headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}
    payload = {"inputs": text, "options": {"wait_for_model": True}}

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

        raw = resp.json()
        # HF feature-extraction returns shape [tokens x dims] or [1 x dims]; take first row
        if isinstance(raw[0], list):
            raw = raw[0]

        vector = np.array(raw, dtype=np.float32)
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        cache.set(f"embed:{text}", vector, timeout=None)
        return vector

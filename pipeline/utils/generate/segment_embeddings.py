import json
from datetime import datetime, timezone

from django.conf import settings

from pipeline.log import Log
from pipeline.utils.http import pipeline_session, server_url


def generate_segment_embeddings(options: dict, log: Log) -> None:
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/unsegmented-beat-segments/"))
    resp.raise_for_status()
    segments = resp.json().get("segments", [])

    if not segments:
        log("No beat segments need embeddings.")
        return

    batch_size = options.get("batch_size")
    if batch_size is None:
        batch_size = 32
    if batch_size < 1:
        raise ValueError("--batch-size must be at least 1")

    log(f"{len(segments)} segment(s) to embed. Loading model...")
    from sentence_transformers import SentenceTransformer

    model_kwargs = {}
    if options.get("device"):
        model_kwargs["device"] = options["device"]
    model = SentenceTransformer("all-mpnet-base-v2", **model_kwargs)

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

import json
from datetime import datetime, timezone

from django.conf import settings

from pipeline.utils.http import pipeline_session, server_url
from pipeline.log import Log


def generate_embeddings(options: dict, log: Log) -> None:
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/unembedded-beats/"))
    resp.raise_for_status()
    beats = resp.json().get("beats", [])

    if not beats:
        log("No beats need embeddings.")
        return

    log(f"{len(beats)} beat(s) to embed. Loading model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-mpnet-base-v2")

    log(f"Encoding {len(beats)} text(s)...")
    embeddings = model.encode([b["text"] for b in beats], batch_size=256, show_progress_bar=True).tolist()

    outbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = outbox_dir / f"embeddings_{ts}.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for beat, embedding in zip(beats, embeddings):
            f.write(json.dumps({"key": beat["key"], "embedding": embedding}, separators=(",", ":")) + "\n")

    log.success(f"Written {len(beats)} embeddings to {out_path.name}")

import json
from datetime import datetime, timezone

from django.conf import settings

from pipeline.log import Log
from pipeline.utils.http import pipeline_session, server_url


SEGMENT_FETCH_BATCH_SIZE = 1000
SEGMENT_BUILD_BEATS_PER_FETCH = 200


def generate_segment_embeddings(options: dict, log: Log) -> None:
    segments_url = server_url("/api/pipeline/unsegmented-beat-segments/")

    batch_size = options.get("batch_size")
    if batch_size is None:
        batch_size = 32
    if batch_size < 1:
        raise ValueError("--batch-size must be at least 1")

    log(f"Fetching beat segments from {segments_url} in batches of {SEGMENT_FETCH_BATCH_SIZE}...")
    session = pipeline_session()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    outbox_dir = settings.PIPELINE_DATA_DIR / "segment_embeddings_outbox"
    out_path = outbox_dir / f"segment_embeddings_{ts}.jsonl"

    model = None
    total_written = 0
    after_id = 0
    batch_number = 0

    while True:
        batch_number += 1
        log(f"Fetching segment batch {batch_number} after id {after_id}...")
        resp = session.get(
            segments_url,
            params={
                "after_id": after_id,
                "limit": SEGMENT_FETCH_BATCH_SIZE,
                "build_beats": SEGMENT_BUILD_BEATS_PER_FETCH,
            },
        )
        resp.raise_for_status()
        payload = resp.json()
        segments = payload.get("segments", [])
        next_cursor = payload.get("next_cursor", after_id)
        has_more = payload.get("has_more", False)
        built_beats = payload.get("built_beats")
        build_note = f", built segments for {built_beats} beat(s)" if built_beats is not None else ""
        log(f"Fetched {len(segments)} segment(s){build_note}; has_more={has_more}.")

        if not segments:
            if total_written == 0:
                log("No beat segments need embeddings.")
                return
            break

        if model is None:
            log("Loading model all-mpnet-base-v2...")
            from sentence_transformers import SentenceTransformer

            model_kwargs = {}
            if options.get("device"):
                model_kwargs["device"] = options["device"]
            model = SentenceTransformer("all-mpnet-base-v2", **model_kwargs)
            log("Model loaded.")

        total_batches = (len(segments) + batch_size - 1) // batch_size
        log(f"Encoding batch {batch_number}: {len(segments)} text(s) with batch size {batch_size} ({total_batches} encoder batch(es))...")
        embeddings = model.encode([s["text"] for s in segments], batch_size=batch_size, show_progress_bar=True).tolist()
        outbox_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("a", encoding="utf-8") as f:
            for segment, embedding in zip(segments, embeddings):
                f.write(json.dumps({"key": segment["key"], "embedding": embedding}, separators=(",", ":")) + "\n")
        total_written += len(segments)
        log(f"Batch {batch_number} written. Total segment embeddings written: {total_written}.")

        if not has_more:
            break
        if next_cursor <= after_id:
            log.warning("Segment cursor did not advance; stopping to avoid refetching the same batch.")
            break
        after_id = next_cursor

    log.success(f"Written {total_written} segment embeddings to {out_path.name}")

import json
import shutil
from datetime import datetime, timezone

from django.conf import settings

from pipeline.local_utils.http import pipeline_session, server_url


def generate_embeddings(options: dict, stdout=None, style=None) -> None:
    """Fetch unembedded beats from server, compute embeddings, write to embeddings_outbox/."""
    session = pipeline_session()
    resp = session.get(server_url("/api/pipeline/unembedded-beats/"))
    resp.raise_for_status()
    beats = resp.json().get("beats", [])

    if not beats:
        if stdout:
            stdout.write("No beats need embeddings.")
        return

    if stdout:
        stdout.write(f"{len(beats)} beat(s) to embed. Loading model...")

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-mpnet-base-v2")
    texts = [b["text"] for b in beats]

    if stdout:
        stdout.write(f"Encoding {len(texts)} text(s)...")
    embeddings = model.encode(texts, batch_size=256, show_progress_bar=True).tolist()

    outbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = outbox_dir / f"embeddings_{ts}.jsonl"

    with out_path.open("w", encoding="utf-8") as f:
        for beat, embedding in zip(beats, embeddings):
            f.write(json.dumps({"key": beat["key"], "embedding": embedding}, separators=(",", ":")) + "\n")

    if stdout:
        stdout.write(
            style.SUCCESS(f"Written {len(beats)} embeddings to {out_path.name}") if style
            else f"Written {out_path.name}"
        )


def upload_embeddings(options: dict, stdout=None, style=None) -> None:
    outbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_outbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "embeddings_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(outbox_dir.glob("*.jsonl")) if outbox_dir.exists() else []
    if not files:
        if stdout:
            stdout.write("No files in embeddings_outbox/")
        return

    session = pipeline_session()
    total_stored = total_failed = 0

    for path in files:
        resp = session.post(
            server_url("/api/pipeline/embeddings/"),
            data=path.read_bytes(),
            headers={"Content-Type": "application/x-ndjson"},
        )
        result = resp.json() if resp.content else {}
        if resp.status_code in (200, 202):
            shutil.move(str(path), archive_dir / path.name)
            total_stored += result.get("stored", 0)
            if stdout:
                stdout.write(f"  {path.name}: stored={result.get('stored')}, not_found={result.get('not_found')}")
        else:
            total_failed += 1
            if stdout:
                stdout.write(style.ERROR(f"  {path.name}: {result.get('error', resp.text)}") if style else f"  {path.name}: failed")

    if stdout:
        stdout.write(f"Done. {total_stored} embeddings stored, {total_failed} files failed.")

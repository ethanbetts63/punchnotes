import json
import re
import shutil

from django.conf import settings

from pipeline.models import Beat


def _parse_key(key: str) -> dict | None:
    m = re.fullmatch(r"ep(\d+)\.set(\d+)\.bit(\d+)\.beat(\d+)", key)
    if not m:
        return None
    return {
        "episode_number": int(m.group(1)),
        "set_number": int(m.group(2)),
        "bit_number": int(m.group(3)),
        "beat_number": int(m.group(4)),
    }


def unembedded_beats() -> list[dict]:
    """Return beats missing embeddings with their stable composite key and embedding text."""
    from pipeline.management.commands.generate_embeddings import _embedding_text, _load_lines_by_set

    beats = list(
        Beat.objects
        .filter(embedding=[])
        .exclude(joke_type=None)
        .exclude(joke_type="")
        .select_related("bit__set__video")
        .only(
            "id", "beat_id", "line_start", "line_end", "joke_type", "embedding",
            "bit__bit_id", "bit__set_id",
            "bit__set__set_number", "bit__set__video__number",
        )
        .order_by("bit__set__video__number", "bit__set__set_number")
    )
    if not beats:
        return []

    lines_by_set = _load_lines_by_set(beats)
    result = []
    for beat in beats:
        text = _embedding_text(beat, lines_by_set=lines_by_set)
        if not text:
            continue
        set_obj = beat.bit.set
        ep_num = set_obj.video.number
        set_num = set_obj.set_number
        bit_m = re.search(r"(\d+)$", beat.bit.bit_id)
        beat_m = re.search(r"(\d+)$", beat.beat_id)
        if not bit_m or not beat_m:
            continue
        bit_num = int(bit_m.group(1))
        beat_num = int(beat_m.group(1))
        result.append({
            "key": f"ep{ep_num}.set{set_num:02d}.bit{bit_num:03d}.beat{beat_num:03d}",
            "text": text,
        })
    return result


def ingest_embeddings(pairs: list[dict]) -> dict:
    """
    pairs: [{"key": "ep764.set02.bit003.beat001", "embedding": [...]}, ...]
    Resolves the stable key to a DB PK and writes the embedding.
    """
    stored = not_found = invalid_key = 0
    updates = []

    for pair in pairs:
        key = pair.get("key", "")
        embedding = pair.get("embedding", [])
        parsed = _parse_key(key)
        if parsed is None:
            invalid_key += 1
            continue

        bit_id = f"bit_{parsed['bit_number']:03d}"
        beat_id = f"bit_{parsed['bit_number']:03d}_beat_{parsed['beat_number']:03d}"

        try:
            beat = Beat.objects.get(
                beat_id=beat_id,
                bit__bit_id=bit_id,
                bit__set__set_number=parsed["set_number"],
                bit__set__video__number=parsed["episode_number"],
            )
            beat.embedding = embedding
            updates.append(beat)
        except Beat.DoesNotExist:
            not_found += 1

    if updates:
        Beat.objects.bulk_update(updates, ["embedding"], batch_size=500)
        stored = len(updates)

    return {"stored": stored, "not_found": not_found, "invalid_key": invalid_key}


def run_update_embeddings(stdout=None, style=None) -> None:
    inbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_inbox"
    archive_dir = settings.PIPELINE_DATA_DIR / "embeddings_archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(inbox_dir.glob("*.jsonl")) if inbox_dir.exists() else []
    if not files:
        if stdout:
            stdout.write("No files in embeddings_inbox/")
        return

    total = {"stored": 0, "not_found": 0, "invalid_key": 0}
    for path in files:
        pairs = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                pairs.append(json.loads(line))
            except json.JSONDecodeError:
                total["invalid_key"] += 1
        result = ingest_embeddings(pairs)
        for k in total:
            total[k] += result.get(k, 0)
        shutil.move(str(path), archive_dir / path.name)
        if stdout:
            stdout.write(f"  {path.name}: {result}")

    if stdout:
        stdout.write(style.SUCCESS(f"Done. {total}") if style else f"Done. {total}")

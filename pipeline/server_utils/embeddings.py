import json
import re
from pathlib import Path

from django.conf import settings

from pipeline.log import Log
from pipeline.models import Beat
from pipeline.server_utils.inbox import run_inbox_update


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
        result.append({
            "key": f"ep{ep_num}.set{set_num:02d}.bit{int(bit_m.group(1)):03d}.beat{int(beat_m.group(1)):03d}",
            "text": text,
        })
    return result


def ingest_embeddings(pairs: list[dict]) -> dict:
    stored = not_found = invalid_key = 0
    updates = []
    for pair in pairs:
        parsed = _parse_key(pair.get("key", ""))
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
            beat.embedding = pair.get("embedding", [])
            updates.append(beat)
        except Beat.DoesNotExist:
            not_found += 1
    if updates:
        Beat.objects.bulk_update(updates, ["embedding"], batch_size=500)
        stored = len(updates)
    return {"stored": stored, "not_found": not_found, "invalid_key": invalid_key}


def _process_embeddings_file(path: Path) -> dict:
    pairs = []
    invalid_key = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            pairs.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_key += 1
    result = ingest_embeddings(pairs)
    result["invalid_key"] += invalid_key
    return result


def run_update_embeddings(log: Log | None = None) -> None:
    run_inbox_update(
        inbox_dir=settings.PIPELINE_DATA_DIR / "embeddings_inbox",
        archive_dir=settings.PIPELINE_DATA_DIR / "embeddings_archive",
        process_fn=_process_embeddings_file,
        log=log,
    )

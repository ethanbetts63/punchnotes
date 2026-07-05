import json
import re
from pathlib import Path

from django.conf import settings

from pipeline.log import Log
from pipeline.models import Beat, BeatSegment, Line
from pipeline.utils.inbox import run_inbox_update
from pipeline.utils.segmenting import segment_beat_lines


def _load_all_lines_by_set(beats: list) -> dict:
    set_ids = {beat.bit.set_id for beat in beats}
    if not set_ids:
        return {}
    lines_by_set: dict = {}
    lines = (
        Line.objects
        .filter(set_id__in=set_ids)
        .order_by("set_id", "line_number")
        .values_list("set_id", "line_number", "text")
    )
    for set_id, line_number, text in lines:
        lines_by_set.setdefault(set_id, []).append((line_number, text))
    return lines_by_set


def ensure_beat_segments(beats: list) -> None:
    beats = list(beats)
    if not beats:
        return

    already_segmented = set(
        BeatSegment.objects
        .filter(beat_id__in=[beat.id for beat in beats])
        .values_list("beat_id", flat=True)
        .distinct()
    )
    beats = [beat for beat in beats if beat.id not in already_segmented]
    if not beats:
        return

    lines_by_set = _load_all_lines_by_set(beats)
    segments_to_create = []
    for beat in beats:
        set_id = beat.bit.set_id
        beat_lines = [
            (line_number, text)
            for line_number, text in lines_by_set.get(set_id, [])
            if beat.line_start <= line_number <= beat.line_end
        ]
        for ordinal, segment in enumerate(segment_beat_lines(beat_lines), start=1):
            segments_to_create.append(BeatSegment(
                beat=beat,
                ordinal=ordinal,
                text=segment.text,
                line_start=segment.line_start,
                line_end=segment.line_end,
            ))

    BeatSegment.objects.bulk_create(segments_to_create)


def _parse_segment_key(key: str) -> dict | None:
    m = re.fullmatch(r"ep(\d+)\.set(\d+)\.bit(\d+)\.beat(\d+)\.seg(\d+)", key)
    if not m:
        return None
    return {
        "episode_number": int(m.group(1)),
        "set_number": int(m.group(2)),
        "bit_number": int(m.group(3)),
        "beat_number": int(m.group(4)),
        "segment_ordinal": int(m.group(5)),
    }


def unembedded_beat_segments() -> list[dict]:
    beats = list(
        Beat.objects
        .exclude(joke_type=None)
        .exclude(joke_type="")
        .select_related("bit__set__video")
        .only(
            "id", "beat_id", "line_start", "line_end", "joke_type",
            "bit__bit_id", "bit__set_id",
            "bit__set__set_number", "bit__set__video__number",
        )
        .order_by("bit__set__video__number", "bit__set__set_number")
    )
    if not beats:
        return []

    ensure_beat_segments(beats)

    result = []
    segments = (
        BeatSegment.objects
        .filter(beat__in=beats, embedding=[])
        .select_related("beat__bit__set__video")
        .order_by("beat__bit__set__video__number", "beat__bit__set__set_number", "beat_id", "ordinal")
    )
    for segment in segments:
        beat = segment.beat
        set_obj = beat.bit.set
        ep_num = set_obj.video.number
        set_num = set_obj.set_number
        bit_m = re.search(r"(\d+)$", beat.bit.bit_id)
        beat_m = re.search(r"(\d+)$", beat.beat_id)
        if not bit_m or not beat_m:
            continue
        key = (
            f"ep{ep_num}.set{set_num:02d}.bit{int(bit_m.group(1)):03d}"
            f".beat{int(beat_m.group(1)):03d}.seg{segment.ordinal:03d}"
        )
        result.append({"key": key, "text": segment.text})
    return result


def ingest_segment_embeddings(pairs: list[dict]) -> dict:
    stored = not_found = invalid_key = 0
    updates = []
    for pair in pairs:
        parsed = _parse_segment_key(pair.get("key", ""))
        if parsed is None:
            invalid_key += 1
            continue
        bit_id = f"bit_{parsed['bit_number']:03d}"
        beat_id = f"bit_{parsed['bit_number']:03d}_beat_{parsed['beat_number']:03d}"
        try:
            segment = BeatSegment.objects.get(
                ordinal=parsed["segment_ordinal"],
                beat__beat_id=beat_id,
                beat__bit__bit_id=bit_id,
                beat__bit__set__set_number=parsed["set_number"],
                beat__bit__set__video__number=parsed["episode_number"],
            )
            segment.embedding = pair.get("embedding", [])
            updates.append(segment)
        except BeatSegment.DoesNotExist:
            not_found += 1
    if updates:
        BeatSegment.objects.bulk_update(updates, ["embedding"], batch_size=500)
        stored = len(updates)
    return {"stored": stored, "not_found": not_found, "invalid_key": invalid_key}


def _process_segment_embeddings_file(path: Path) -> dict:
    pairs = []
    invalid_key = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            pairs.append(json.loads(line))
        except json.JSONDecodeError:
            invalid_key += 1
    result = ingest_segment_embeddings(pairs)
    result["invalid_key"] += invalid_key
    return result


def run_update_segment_embeddings(log: Log, archive: bool = False) -> None:
    if archive:
        source_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive"
        if not source_dir.exists():
            log("No segment_embeddings_archive/ dir.")
            return
        files = sorted(source_dir.glob("*.jsonl"))
        if not files:
            log("No files in segment_embeddings_archive/")
            return
        for path in files:
            result = _process_segment_embeddings_file(path)
            log(f"  {path.name}: {result['stored']} stored, {result['not_found']} not found")
        log.success(f"Done. {len(files)} file(s) processed.")
    else:
        run_inbox_update(
            inbox_dir=settings.PIPELINE_DATA_DIR / "segment_embeddings_inbox",
            archive_dir=settings.PIPELINE_PRIVATE_DATA_DIR / "segment_embeddings_archive",
            process_fn=_process_segment_embeddings_file,
            log=log,
        )

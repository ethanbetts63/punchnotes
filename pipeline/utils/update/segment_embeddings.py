import json
import re
from pathlib import Path

from django.conf import settings
from django.db.models import Count

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
        .values_list("set_id", "line_number", "text", "label")
    )
    for set_id, line_number, text, label in lines:
        lines_by_set.setdefault(set_id, []).append((line_number, text, label))
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
            for line_number, text, label in lines_by_set.get(set_id, [])
            if beat.line_start <= line_number <= beat.line_end and label != "fluff"
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
    m = re.fullmatch(r"ep(\d+)\.ts(\d+)\.bit(\d+)\.beat(\d+)\.seg(\d+)", key)
    if not m:
        return None
    return {
        "episode_number": int(m.group(1)),
        "start_seconds": int(m.group(2)),
        "bit_number": int(m.group(3)),
        "beat_number": int(m.group(4)),
        "segment_ordinal": int(m.group(5)),
    }


def _candidate_beats():
    return (
        Beat.objects
        .exclude(joke_type=None)
        .exclude(joke_type="")
        .select_related("bit__set__video")
        .only(
            "id", "beat_id", "line_start", "line_end", "joke_type",
            "bit__bit_id", "bit__set_id",
            "bit__set__start_seconds", "bit__set__video__number",
        )
        .order_by("bit__set__video__number", "bit__set__start_seconds")
    )


def _segment_payload(segment: BeatSegment) -> dict | None:
    beat = segment.beat
    set_obj = beat.bit.set
    ep_num = set_obj.video.number
    start_secs = int(set_obj.start_seconds)
    bit_m = re.search(r"(\d+)$", beat.bit.bit_id)
    beat_m = re.search(r"(\d+)$", beat.beat_id)
    if not bit_m or not beat_m:
        return None
    key = (
        f"ep{ep_num}.ts{start_secs}.bit{int(bit_m.group(1)):03d}"
        f".beat{int(beat_m.group(1)):03d}.seg{segment.ordinal:03d}"
    )
    return {"id": segment.id, "key": key, "text": segment.text}


def unembedded_beat_segments() -> list[dict]:
    beats = list(_candidate_beats())
    if not beats:
        return []

    ensure_beat_segments(beats)

    result = []
    segments = (
        BeatSegment.objects
        .filter(beat__in=beats, embedding=[])
        .select_related("beat__bit__set__video")
        .order_by("beat__bit__set__video__number", "beat__bit__set__start_seconds", "beat_id", "ordinal")
    )
    for segment in segments:
        payload = _segment_payload(segment)
        if payload is not None:
            result.append({"key": payload["key"], "text": payload["text"]})
    return result


def unembedded_beat_segments_batch(after_id: int = 0, limit: int = 500, build_beats: int = 200) -> dict:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    if build_beats < 0:
        raise ValueError("build_beats cannot be negative")

    beats_to_segment = list(
        _candidate_beats()
        .annotate(segment_count=Count("segments"))
        .filter(segment_count=0)[:build_beats]
    )
    ensure_beat_segments(beats_to_segment)

    segments_qs = (
        BeatSegment.objects
        .filter(embedding=[], id__gt=after_id)
        .exclude(beat__joke_type=None)
        .exclude(beat__joke_type="")
        .select_related("beat__bit__set__video")
        .order_by("id")[:limit]
    )
    segments = []
    next_cursor = after_id
    for segment in segments_qs:
        next_cursor = max(next_cursor, segment.id)
        payload = _segment_payload(segment)
        if payload is not None:
            segments.append(payload)

    has_more_segments = BeatSegment.objects.filter(embedding=[], id__gt=next_cursor).exists()
    has_more_unsegmented_beats = (
        _candidate_beats()
        .annotate(segment_count=Count("segments"))
        .filter(segment_count=0)
        .exists()
    )
    return {
        "segments": segments,
        "next_cursor": next_cursor,
        "built_beats": len(beats_to_segment),
        "has_more": has_more_segments or has_more_unsegmented_beats,
    }


def ingest_segment_embeddings(pairs: list[dict]) -> dict:
    stored = not_found = invalid_key = 0
    parsed_pairs = []
    episode_numbers = set()
    bit_ids = set()
    beat_ids = set()
    segment_ordinals = set()

    for pair in pairs:
        parsed = _parse_segment_key(pair.get("key", ""))
        if parsed is None:
            invalid_key += 1
            continue
        bit_id = f"bit_{parsed['bit_number']:03d}"
        beat_id = f"bit_{parsed['bit_number']:03d}_beat_{parsed['beat_number']:03d}"
        lookup_key = (
            parsed["episode_number"],
            parsed["start_seconds"],
            bit_id,
            beat_id,
            parsed["segment_ordinal"],
        )
        parsed_pairs.append((lookup_key, pair.get("embedding", [])))
        episode_numbers.add(parsed["episode_number"])
        bit_ids.add(bit_id)
        beat_ids.add(beat_id)
        segment_ordinals.add(parsed["segment_ordinal"])

    if not parsed_pairs:
        return {"stored": stored, "not_found": not_found, "invalid_key": invalid_key}

    candidate_segments = (
        BeatSegment.objects
        .filter(
            ordinal__in=segment_ordinals,
            beat__beat_id__in=beat_ids,
            beat__bit__bit_id__in=bit_ids,
            beat__bit__set__video__number__in=episode_numbers,
        )
        .select_related("beat__bit__set__video")
    )
    segments_by_key = {}
    for segment in candidate_segments:
        beat = segment.beat
        lookup_key = (
            beat.bit.set.video.number,
            int(beat.bit.set.start_seconds),
            beat.bit.bit_id,
            beat.beat_id,
            segment.ordinal,
        )
        segments_by_key[lookup_key] = segment

    updates = []
    seen_segment_ids = set()
    for lookup_key, embedding in parsed_pairs:
        segment = segments_by_key.get(lookup_key)
        if segment is None:
            not_found += 1
            continue
        if segment.id in seen_segment_ids:
            continue
        segment.embedding = embedding
        updates.append(segment)
        seen_segment_ids.add(segment.id)

    if updates:
        BeatSegment.objects.bulk_update(updates, ["embedding"], batch_size=1000)
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


def run_update_segment_embeddings(log: Log) -> None:
    run_inbox_update(
        inbox_dir=settings.PIPELINE_DATA_DIR / "segment_embeddings_inbox",
        process_fn=_process_segment_embeddings_file,
        log=log,
    )

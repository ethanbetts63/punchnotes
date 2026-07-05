import json
import time
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations

import numpy as np
from django.conf import settings
from django.utils import timezone

from pipeline.log import Log
from pipeline.models import Beat, Line
from pipeline.utils.report_format import format_report_json

OUTPUT_FILENAME = "embedding_similarity_report.json"
DEFAULT_THRESHOLD = 0.70


@dataclass(frozen=True)
class BeatRecord:
    id: int
    joke_type: str | None
    created_at: datetime
    premise: str | None
    line_start: int
    line_end: int
    set_id: int
    comedian_id: int
    comedian_name: str
    vector: np.ndarray


def _cosine_sim(a, b):
    return float(np.dot(a, b))


def _normalized_vector(embedding):
    vector = np.asarray(embedding, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def _parse_report(report_path):
    if not report_path.exists():
        return None
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {"generated_at": None, "threshold": None, "pairs": payload}
    return payload


def _pair_key(beat_a_id, beat_b_id):
    return tuple(sorted((beat_a_id, beat_b_id)))


def _parse_timestamp(value):
    if not value:
        return None
    return datetime.fromisoformat(value)


def _build_beat_records(qs):
    records = []
    for beat in qs:
        records.append(BeatRecord(
            id=beat.id,
            joke_type=beat.joke_type,
            created_at=beat.created_at,
            premise=beat.premise,
            line_start=beat.line_start,
            line_end=beat.line_end,
            set_id=beat.bit.set_id,
            comedian_id=beat.bit.set.comedian_id,
            comedian_name=beat.bit.set.comedian.name,
            vector=_normalized_vector(beat.embedding),
        ))
    return records


def _fetch_lines_for_beats(beats):
    beats = list(beats)
    if not beats:
        return {}
    set_ids = {beat.set_id for beat in beats}
    lines_by_set = {}
    lines = (
        Line.objects
        .filter(set_id__in=set_ids, label__in=("setup", "punchline", "tag"))
        .order_by("set_id", "line_number")
        .values("set_id", "line_number", "label", "text")
    )
    for line in lines:
        lines_by_set.setdefault(line["set_id"], []).append(line)
    result = {}
    for beat in beats:
        beat_lines = []
        for line in lines_by_set.get(beat.set_id, []):
            if beat.line_start <= line["line_number"] <= beat.line_end:
                beat_lines.append({"label": line["label"], "text": line["text"]})
        result[beat.id] = beat_lines
    return result


def generate_embeddings_report(log: Log) -> None:
    threshold = DEFAULT_THRESHOLD
    output_path = settings.PIPELINE_PRIVATE_DATA_DIR / OUTPUT_FILENAME
    existing_report = _parse_report(output_path)
    generated_at = timezone.now()

    full_rebuild = existing_report is None
    last_generated_at = None
    existing_pairs = []

    if existing_report is not None:
        existing_pairs = existing_report.get("pairs", [])
        last_generated_at = _parse_timestamp(existing_report.get("generated_at"))
        prior_threshold = existing_report.get("threshold")
        if prior_threshold is None:
            full_rebuild = True
            log("Existing report has no threshold metadata. Rebuilding from scratch.")
        elif float(prior_threshold) != threshold:
            full_rebuild = True
            log(f"Existing report threshold {prior_threshold} differs from requested {threshold}. Rebuilding from scratch.")
        elif last_generated_at is None:
            full_rebuild = True
            log("Existing report has no generated_at metadata. Rebuilding from scratch.")

    qs = Beat.objects.exclude(embedding=[]).select_related("bit__set__comedian")
    beats = _build_beat_records(qs)
    log(f"Loaded {len(beats)} beats with embeddings.")
    if not beats:
        inbox_dir = settings.PIPELINE_DATA_DIR / "embeddings_inbox"
        archive_dir = settings.PIPELINE_PRIVATE_DATA_DIR / "embeddings_archive"
        if inbox_dir.exists() and any(inbox_dir.glob("*.jsonl")):
            log.warning("Embedding files are queued in embeddings_inbox/. Run `python manage.py update --embeddings` first.")
        elif archive_dir.exists() and any(archive_dir.glob("*.jsonl")):
            log.warning("No embeddings are stored in this database. To load local archived embeddings, run `python manage.py update --embeddings --archive` first.")
        else:
            log.warning("No embeddings are stored in this database. Run `python manage.py generate --embeddings` and ingest them before generating a report.")
        return

    if not full_rebuild and last_generated_at is not None:
        new_beats = [beat for beat in beats if beat.created_at > last_generated_at]
        if not new_beats:
            report = {"generated_at": generated_at.isoformat(), "threshold": threshold, "pairs": existing_pairs}
            output_path.write_text(format_report_json(report), encoding="utf-8")
            log.success(f"\nNo new beats since {last_generated_at}. Report timestamp refreshed at {output_path}")
            return
        log(f"Found {len(new_beats)} new beats since {last_generated_at}. Running incremental comparison.")
    else:
        new_beats = beats

    groups: dict[str, list] = {}
    for beat in beats:
        groups.setdefault(beat.joke_type or "unknown", []).append(beat)

    new_ids = {beat.id for beat in new_beats}
    REPORT_EVERY = 100_000

    raw_pairs = []
    for label, group in groups.items():
        if full_rebuild:
            candidate_pairs = combinations(group, 2)
            n_pairs = len(group) * (len(group) - 1) // 2
        else:
            candidate_pairs = (
                (a, b)
                for a, b in combinations(group, 2)
                if a.id in new_ids or b.id in new_ids
            )
            old_count = len(group) - sum(1 for beat in group if beat.id in new_ids)
            new_count = len(group) - old_count
            n_pairs = (new_count * old_count) + (new_count * (new_count - 1) // 2)

        if n_pairs == 0:
            continue

        log(f"\n  {label}: {len(group)} beats, {n_pairs:,} pairs")
        group_start = time.time()
        checked = 0
        found = 0
        for a, b in candidate_pairs:
            checked += 1
            if a.comedian_id == b.comedian_id:
                continue
            sim = round(_cosine_sim(a.vector, b.vector), 4)
            if sim >= threshold:
                raw_pairs.append((sim, a, b))
                found += 1
            if checked % REPORT_EVERY == 0:
                elapsed = time.time() - group_start
                rate = checked / elapsed
                remaining = (n_pairs - checked) / rate
                log(
                    f"    {checked:,}/{n_pairs:,} ({100 * checked / n_pairs:.1f}%) | "
                    f"{found} found | {elapsed:.0f}s elapsed | ~{remaining:.0f}s left"
                )
        elapsed = time.time() - group_start
        log(f"  Done: {found} pairs found in {elapsed:.1f}s")

    if full_rebuild:
        merged_pairs = []
    else:
        matched_new_pair_keys = {
            _pair_key(pair["beat_a"]["id"], pair["beat_b"]["id"])
            for pair in existing_pairs
            if pair["beat_a"]["id"] not in new_ids and pair["beat_b"]["id"] not in new_ids
        }
        merged_pairs = [
            pair for pair in existing_pairs
            if _pair_key(pair["beat_a"]["id"], pair["beat_b"]["id"]) in matched_new_pair_keys
        ]

    lines_by_beat = {}
    if raw_pairs:
        matched_beats = {beat.id: beat for _, a, b in raw_pairs for beat in (a, b)}
        log(f"\nFetching lines for {len(matched_beats)} matched beats...")
        lines_by_beat = _fetch_lines_for_beats(matched_beats.values())

    new_pairs = []
    for sim, a, b in raw_pairs:
        new_pairs.append({
            "similarity": sim,
            "beat_a": {
                "id": a.id,
                "joke_type": a.joke_type,
                "comedian": a.comedian_name,
                "premise": a.premise,
                "lines": lines_by_beat.get(a.id, []),
            },
            "beat_b": {
                "id": b.id,
                "joke_type": b.joke_type,
                "comedian": b.comedian_name,
                "premise": b.premise,
                "lines": lines_by_beat.get(b.id, []),
            },
        })

    merged_pairs.extend(new_pairs)
    merged_pairs.sort(key=lambda p: p["similarity"], reverse=True)

    report = {"generated_at": generated_at.isoformat(), "threshold": threshold, "pairs": merged_pairs}
    output_path.write_text(format_report_json(report), encoding="utf-8")

    log.success(
        f"\nFound {len(new_pairs)} new pairs above threshold {threshold}. "
        f"Stored {len(merged_pairs)} total pairs. "
        f"Written to {output_path}"
    )

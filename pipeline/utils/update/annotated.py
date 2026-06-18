from django.db import transaction

from pipeline.utils.comedian_aliases import canonicalize_comedian_name, load_relationships
from pipeline.utils.update.records import (
    import_bits,
    import_lines,
    refresh_comedian_stats,
    refresh_episode_counts,
    get_video_for_set,
    upsert_comedian,
    upsert_set,
)
from pipeline.json_validation import validate_bit_meta
from pipeline.models import Comedian, Video
from pipeline.utils.similar_comedians import update_candidate_report


def ingest_annotated_set(data: dict, relationships: dict | None = None, defer_refresh: bool = False) -> dict:
    if relationships is None:
        relationships = load_relationships()

    validate_bit_meta(data)

    video_id = data["video_id"]
    canonical_comedian = canonicalize_comedian_name(data["comedian_name"], relationships)
    data = {**data, "comedian_name": canonical_comedian.name}

    video = get_video_for_set(video_id)
    comedian = upsert_comedian(canonical_comedian.slug, data)

    with transaction.atomic():
        set_obj = upsert_set(video, comedian, data)

        lines = import_lines(set_obj, data["lines"])
        import_bits(set_obj, data["lines"], data.get("bit_meta", {}))

        if not defer_refresh:
            refresh_comedian_stats(comedian)
            refresh_episode_counts(video)

    if not defer_refresh:
        all_comedians = list(Comedian.objects.order_by("slug").values_list("name", "slug"))
        update_candidate_report((comedian.name, comedian.slug), all_comedians, relationships)

    return {
        "status": "ok",
        "video_id": video_id,
        "set_number": set_obj.set_number,
        "comedian": canonical_comedian.name,
        "lines": len(lines),
        "bits": len(data.get("bit_meta", {})),
    }


def refresh_all_stats() -> None:
    from pipeline.utils.similar_comedians import find_candidates, write_candidate_report
    relationships = load_relationships()
    for comedian in Comedian.objects.all():
        refresh_comedian_stats(comedian)
    for video in Video.objects.all():
        refresh_episode_counts(video)
    all_comedians = list(Comedian.objects.order_by("slug").values_list("name", "slug"))
    candidates = find_candidates(all_comedians, 80.0, relationships)
    write_candidate_report(candidates)

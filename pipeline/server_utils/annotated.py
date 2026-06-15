from django.db import transaction

from pipeline.import_utils.comedian_aliases import canonicalize_comedian_name, load_relationships
from pipeline.import_utils.records import (
    import_bits,
    import_lines,
    refresh_episode_counts,
    upsert_comedian,
    upsert_episode,
    upsert_set,
)
from pipeline.json_validation import validate_bit_meta
from pipeline.models import Comedian
from pipeline.management.commands.find_similar_comedians import find_candidates, write_candidate_report


def ingest_annotated_set(data: dict, relationships: dict | None = None) -> dict:
    """
    Ingest a single annotated set dict into the DB.
    Returns {"status": "ok", "video_id", "set_number", "comedian", "lines", "bits"}
    or raises on validation/import error.
    """
    if relationships is None:
        relationships = load_relationships()

    validate_bit_meta(data)

    video_id = data["video_id"]
    canonical_comedian = canonicalize_comedian_name(data["comedian_name"], relationships)
    data = {**data, "comedian_name": canonical_comedian.name}

    episode = upsert_episode(video_id, data)
    comedian = upsert_comedian(canonical_comedian.slug, data)

    with transaction.atomic():
        set_obj = upsert_set(episode, comedian, data)

        for guest_name in data.get("guests", []):
            canonical_guest = canonicalize_comedian_name(guest_name, relationships)
            guest, _ = Comedian.objects.get_or_create(
                slug=canonical_guest.slug,
                defaults={"name": canonical_guest.name},
            )
            episode.guests.add(guest)

        lines = import_lines(set_obj, data["lines"])
        import_bits(set_obj, data["lines"], data.get("bit_meta", {}))
        refresh_episode_counts(episode)

    comedians = list(Comedian.objects.order_by("slug").values_list("name", "slug"))
    candidates = find_candidates(comedians, 80.0)
    write_candidate_report(candidates)

    return {
        "status": "ok",
        "video_id": video_id,
        "set_number": set_obj.set_number,
        "comedian": canonical_comedian.name,
        "lines": len(lines),
        "bits": len(data.get("bit_meta", {})),
    }

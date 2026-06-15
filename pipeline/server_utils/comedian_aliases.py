import json
from pathlib import Path

from django.conf import settings
from django.db import transaction

from pipeline.import_utils.comedian_aliases import (
    alias_target,
    relationships_path,
    validate_relationships,
)
from pipeline.import_utils.records import merge_attributes, refresh_comedian_image, refresh_comedian_stats
from pipeline.models import Comedian, Set


def dedup_comedians(relationships: dict, stdout=None) -> dict:
    """
    For each alias → canonical mapping, merge the alias Comedian row into the
    canonical row. Combines attributes, re-points all Sets and guest M2M relations,
    copies image if canonical has none, then deletes the alias record.
    """
    aliases = relationships.get("aliases", {})
    merged = renamed = skipped = not_found = 0

    for alias_slug, target in aliases.items():
        canonical = alias_target(target)

        try:
            alias_comedian = Comedian.objects.get(slug=alias_slug)
        except Comedian.DoesNotExist:
            not_found += 1
            continue

        if alias_comedian.slug == canonical.slug:
            skipped += 1
            continue

        try:
            canonical_comedian = Comedian.objects.get(slug=canonical.slug)
        except Comedian.DoesNotExist:
            alias_comedian.slug = canonical.slug
            alias_comedian.name = canonical.name
            alias_comedian.save(update_fields=["slug", "name"])
            renamed += 1
            if stdout:
                stdout.write(f"  Renamed {alias_slug} -> {canonical.slug}")
            continue

        with transaction.atomic():
            merged_attrs = merge_attributes(canonical_comedian.attributes, alias_comedian.attributes)
            if merged_attrs != canonical_comedian.attributes:
                canonical_comedian.attributes = merged_attrs

            Set.objects.filter(comedian=alias_comedian).update(comedian=canonical_comedian)

            for video in list(alias_comedian.guest_appearances.all()):
                video.guests.remove(alias_comedian)
                video.guests.add(canonical_comedian)

            if not canonical_comedian.image_url and alias_comedian.image_url:
                canonical_comedian.image_url = alias_comedian.image_url
                canonical_comedian.image_set = alias_comedian.image_set

            canonical_comedian.save()
            alias_comedian.delete()

        refresh_comedian_stats(canonical_comedian)
        refresh_comedian_image(canonical_comedian)
        merged += 1
        if stdout:
            stdout.write(f"  Merged {alias_slug} -> {canonical.slug}")

    return {"merged": merged, "renamed": renamed, "skipped": skipped, "not_found": not_found}


def apply_relationships_file(path: Path, stdout=None) -> dict:
    """Load new relationships, save to server data dir, then dedup the DB."""
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_relationships(data)
    dest = relationships_path()
    dest.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return dedup_comedians(data, stdout=stdout)


def run_update_comedian_aliases(stdout=None, style=None) -> None:
    inbox_dir = settings.PIPELINE_DATA_DIR / "comedian_aliases_inbox"
    if not inbox_dir.exists() or not list(inbox_dir.glob("*.json")):
        if stdout:
            stdout.write("No files in comedian_aliases_inbox/")
        return

    path = inbox_dir / "comedian_name_relationships.json"
    if not path.exists():
        path = sorted(inbox_dir.glob("*.json"))[-1]

    result = apply_relationships_file(path, stdout=stdout)
    if stdout:
        stdout.write(
            style.SUCCESS(f"Done. {result}") if style else f"Done. {result}"
        )

import json
from pathlib import Path

from django.conf import settings
from django.db import transaction

from pipeline.utils.comedian_aliases import (
    alias_target,
    relationships_path,
    validate_relationships,
)
from pipeline.utils.set_images import rename_set_image
from pipeline.utils.update.records import merge_attributes, refresh_comedian_image, refresh_comedian_stats
from pipeline.log import Log
from pipeline.models import Comedian, Set


def _rename_comedian_images(comedian: Comedian, new_slug: str) -> None:
    for s in comedian.sets.all():
        new_url = rename_set_image(s, new_comedian_slug=new_slug)
        if new_url is not None and new_url != s.image_url:
            s.image_url = new_url
            s.save(update_fields=["image_url"])


def dedup_comedians(relationships: dict, log: Log) -> dict:
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
            _rename_comedian_images(alias_comedian, canonical.slug)
            alias_comedian.slug = canonical.slug
            alias_comedian.name = canonical.name
            alias_comedian.save(update_fields=["slug", "name"])
            renamed += 1
            log(f"  Renamed {alias_slug} -> {canonical.slug}")
            continue

        _rename_comedian_images(alias_comedian, canonical_comedian.slug)
        with transaction.atomic():
            merged_attrs = merge_attributes(canonical_comedian.attributes, alias_comedian.attributes)
            if merged_attrs != canonical_comedian.attributes:
                canonical_comedian.attributes = merged_attrs
            Set.objects.filter(comedian=alias_comedian).update(comedian=canonical_comedian)
            if not canonical_comedian.image_url and alias_comedian.image_url:
                canonical_comedian.image_url = alias_comedian.image_url
                canonical_comedian.image_set = alias_comedian.image_set
            canonical_comedian.save()
            alias_comedian.delete()

        refresh_comedian_stats(canonical_comedian)
        refresh_comedian_image(canonical_comedian)
        merged += 1
        log(f"  Merged {alias_slug} -> {canonical.slug}")

    return {"merged": merged, "renamed": renamed, "skipped": skipped, "not_found": not_found}


def apply_relationships_file(path: Path, log: Log) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_relationships(data)
    relationships_path().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return dedup_comedians(data, log=log)


def run_update_comedian_aliases(log: Log) -> None:
    inbox_dir = settings.PIPELINE_DATA_DIR / "comedian_aliases_inbox"
    path = inbox_dir / "comedian_name_relationships.json"
    if not path.exists():
        candidates = sorted(inbox_dir.glob("*.json")) if inbox_dir.exists() else []
        if not candidates:
            log("No files in comedian_aliases_inbox/")
            return
        path = candidates[-1]
    result = apply_relationships_file(path, log=log)
    log.success(f"Done. {result}")

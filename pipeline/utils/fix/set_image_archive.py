from pathlib import Path

from django.conf import settings
from django.db.models import ObjectDoesNotExist

from pipeline.log import Log
from pipeline.models import Set
from pipeline.utils.set_images import find_set_for_image, parse_image_name, set_image_media_path
from pipeline.utils.update.records import refresh_comedian_image


def fix_set_image_archive(log: Log, dry_run: bool = False) -> None:
    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    public_dir = settings.MEDIA_ROOT / "set-images"

    if not archive_dir.exists():
        log("No set_images_archive/ dir found.")
        return

    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    files = sorted(p for p in archive_dir.glob("*") if p.suffix.lower() in image_exts)

    if not files:
        log("No images in archive.")
        return

    deleted = skipped = not_found = parse_errors = 0
    prefix = "[dry-run] " if dry_run else ""

    for path in files:
        try:
            parsed = parse_image_name(path)
        except ValueError:
            log.error(f"  {path.name}: could not parse filename")
            parse_errors += 1
            continue

        try:
            set_obj = find_set_for_image(parsed["episode_number"], parsed["start_seconds"])
        except Set.DoesNotExist:
            log.warning(
                f"  {path.name}: no set found for ep {parsed['episode_number']} "
                f"at {parsed['start_seconds']}s"
            )
            not_found += 1
            continue

        if parsed["comic_slug"] == set_obj.comedian.slug:
            skipped += 1
            continue

        log(
            f"  {prefix}{path.name}: slug mismatch "
            f"(file={parsed['comic_slug']!r}, db={set_obj.comedian.slug!r}) — deleting"
        )

        if not dry_run:
            path.unlink()

            public_file = public_dir / path.name
            if public_file.exists():
                public_file.unlink()

            if set_obj.image_url == set_image_media_path(path.name):
                set_obj.image_url = None
                set_obj.save(update_fields=["image_url"])
                refresh_comedian_image(set_obj.comedian)

        deleted += 1

    label = "would delete" if dry_run else "deleted"
    log.success(f"Done. {deleted} {label}, {skipped} correct (skipped), {not_found} set not found, {parse_errors} parse errors.")

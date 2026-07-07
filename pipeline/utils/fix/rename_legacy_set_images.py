import re
from pathlib import Path

from django.conf import settings

from pipeline.log import Log
from pipeline.models import Set
from pipeline.utils.set_images import image_filename, parse_image_name, set_image_media_path
from pipeline.utils.update.records import refresh_comedian_image


LEGACY_IMAGE_NAME_RE = re.compile(
    r"^KT(?P<episode_number>\d+)_set(?P<set_number>\d+)_"
    r"(?P<comic_slug>[a-z0-9][a-z0-9_-]*)\.(?P<ext>jpe?g|png|webp)$",
    re.IGNORECASE,
)


def _parse_legacy_image_name(filename: str) -> dict | None:
    match = LEGACY_IMAGE_NAME_RE.match(filename)
    if not match:
        return None
    return {
        "episode_number": int(match.group("episode_number")),
        "comic_slug": match.group("comic_slug").lower().replace("_", "-"),
        "ext": Path(filename).suffix,
    }


def rename_legacy_set_images(log: Log, dry_run: bool = False) -> None:
    """One-time backfill: rename set-image files from the old KT{ep}_set{NN}_{slug}
    scheme to the new KT{ep}_{start_seconds}_{slug} scheme, using each Set's own
    start_seconds as the source of truth. No re-scraping — pure rename + relink."""
    public_dir = settings.MEDIA_ROOT / "set-images"
    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    prefix = "[dry-run] " if dry_run else ""

    renamed = already_current = unparseable = 0

    sets = Set.objects.exclude(image_url__isnull=True).exclude(image_url="").select_related("comedian")
    for set_obj in sets:
        current_filename = Path(set_obj.image_url).name

        try:
            parse_image_name(Path(current_filename))
            already_current += 1
            continue
        except ValueError:
            pass

        legacy = _parse_legacy_image_name(current_filename)
        if legacy is None:
            log.warning(f"  {current_filename}: does not match legacy or current filename format")
            unparseable += 1
            continue

        new_filename = image_filename(
            legacy["episode_number"], set_obj.start_seconds, legacy["comic_slug"], legacy["ext"]
        )

        log(f"  {prefix}{current_filename} -> {new_filename}")

        if not dry_run:
            old_public = public_dir / current_filename
            if old_public.exists():
                old_public.rename(public_dir / new_filename)

            old_archive = archive_dir / current_filename
            if old_archive.exists():
                old_archive.rename(archive_dir / new_filename)

            set_obj.image_url = set_image_media_path(new_filename)
            set_obj.save(update_fields=["image_url"])
            refresh_comedian_image(set_obj.comedian)

        renamed += 1

    label = "would rename" if dry_run else "renamed"
    log.success(
        f"Done. {renamed} {label}, {already_current} already current, {unparseable} unparseable."
    )

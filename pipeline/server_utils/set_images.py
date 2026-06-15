import shutil
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from pipeline.import_utils.records import refresh_comedian_image
from pipeline.management.commands.import_set_images import parse_image_name, public_image_url
from pipeline.models import Set


def missing_image_sets() -> list[dict]:
    """Return one set per comedian whose image_url is unset, for the local machine to scrape."""
    seen_comedian_ids: set[int] = set()
    result = []

    sets = (
        Set.objects
        .select_related("video", "comedian")
        .filter(Q(comedian__image_url__isnull=True) | Q(comedian__image_url=""))
        .exclude(video__number__isnull=True)
        .order_by("comedian_id", "-video__number", "set_number")
    )
    for s in sets:
        if s.comedian_id not in seen_comedian_ids:
            seen_comedian_ids.add(s.comedian_id)
            result.append({
                "set_id": s.id,
                "video_id": s.video.video_id,
                "episode_number": s.video.number,
                "set_number": s.set_number,
                "comedian_slug": s.comedian.slug,
                "comedian_name": s.comedian.name,
                "start_seconds": s.start_seconds,
            })
    return result


def ingest_set_image(image_path: Path, replace: bool = False) -> str:
    """
    Copy image to public dir, update Set.image_url and Comedian.image_url.
    Returns "imported" or "skipped".
    """
    public_dir = settings.BASE_DIR / "frontend" / "public" / "set-images"
    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    public_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_image_name(image_path)
    set_obj = Set.objects.select_related("video", "comedian").get(
        video__number=parsed["episode_number"],
        set_number=parsed["set_number"],
    )

    if set_obj.comedian.image_url and not replace:
        return "skipped"

    public_path = public_dir / image_path.name
    if public_path.exists() and not replace:
        return "skipped"

    with transaction.atomic():
        shutil.copy2(image_path, public_path)
        set_obj.image_url = public_image_url(image_path.name)
        set_obj.save(update_fields=["image_url"])
        refresh_comedian_image(set_obj.comedian)
        shutil.move(str(image_path), archive_dir / image_path.name)

    return "imported"


def run_update_set_images(stdout=None, style=None) -> None:
    inbox_dir = settings.PIPELINE_DATA_DIR / "set_images_inbox"
    if not inbox_dir.exists():
        if stdout:
            stdout.write("No set_images_inbox/ dir.")
        return

    files = sorted(
        p for p in inbox_dir.glob("*")
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )
    if not files:
        if stdout:
            stdout.write("No images in set_images_inbox/")
        return

    imported = skipped = failed = 0
    for path in files:
        try:
            result = ingest_set_image(path)
            if result == "imported":
                imported += 1
                if stdout:
                    stdout.write(f"  {path.name}: imported")
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            if stdout:
                stdout.write(style.ERROR(f"  {path.name}: {e}") if style else f"  Failed: {e}")

    if stdout:
        stdout.write(
            style.SUCCESS(f"Done. {imported} imported, {skipped} skipped, {failed} failed.") if style
            else f"Done. {imported} imported, {skipped} skipped, {failed} failed."
        )

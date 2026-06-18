import shutil
from pathlib import Path

from django.conf import settings
from django.db import transaction

from pipeline.utils.update.records import refresh_comedian_image
from pipeline.utils.set_images import parse_image_name, set_image_media_path
from pipeline.log import Log
from pipeline.models import Set


def missing_image_sets() -> list[dict]:
    from django.db.models import Q
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


def ingest_set_image(image_path: Path, replace: bool = False, move_to_archive: bool = True) -> str:
    public_dir = settings.MEDIA_ROOT / "set-images"
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
        set_obj.image_url = set_image_media_path(image_path.name)
        set_obj.save(update_fields=["image_url"])
        refresh_comedian_image(set_obj.comedian)
        if move_to_archive:
            shutil.move(str(image_path), archive_dir / image_path.name)

    return "imported"


def _run_images_from_dir(source_dir: Path, replace: bool, move_to_archive: bool, log: Log) -> None:
    image_exts = {".jpg", ".jpeg", ".png", ".webp"}
    files = sorted(p for p in source_dir.glob("*") if p.suffix.lower() in image_exts)
    if not files:
        log(f"No images in {source_dir.name}/")
        return

    imported = skipped = failed = 0
    for path in files:
        try:
            result = ingest_set_image(path, replace=replace, move_to_archive=move_to_archive)
            if result == "imported":
                imported += 1
                log(f"  {path.name}: imported")
            else:
                skipped += 1
        except Exception as e:
            failed += 1
            log.error(f"  {path.name}: {e}")

    log.success(f"Done. {imported} imported, {skipped} skipped, {failed} failed.")


def run_update_set_images(log: Log, archive: bool = False) -> None:
    if archive:
        source_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
        _run_images_from_dir(source_dir, replace=True, move_to_archive=False, log=log)
    else:
        inbox_dir = settings.PIPELINE_DATA_DIR / "set_images_inbox"
        if not inbox_dir.exists():
            log("No set_images_inbox/ dir.")
            return
        _run_images_from_dir(inbox_dir, replace=False, move_to_archive=True, log=log)

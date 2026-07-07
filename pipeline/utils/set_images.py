import re
from pathlib import Path

from django.conf import settings


IMAGE_NAME_RE = re.compile(
    r"^(?P<video_id>[A-Za-z0-9_-]+)_(?P<start_seconds>\d+)_"
    r"(?P<comic_slug>[a-z0-9][a-z0-9_-]*)\.(?P<ext>jpe?g|png|webp)$",
    re.IGNORECASE,
)


def parse_image_name(path: Path) -> dict:
    match = IMAGE_NAME_RE.match(path.name)
    if not match:
        raise ValueError(
            f"Invalid image filename: {path.name}. Expected "
            "{video_id}_{start_seconds}_{slug}.jpg."
        )
    return {
        "video_id": match.group("video_id"),
        "start_seconds": int(match.group("start_seconds")),
        "comic_slug": match.group("comic_slug").lower().replace("_", "-"),
    }


def set_image_media_path(filename: str) -> str:
    """Path stored in Set.image_url, relative to MEDIA_ROOT (e.g. set-images/abc123_100_x.jpg)."""
    return f"set-images/{filename}"


def image_filename(video_id: str, start_seconds: float, comic_slug: str, ext: str) -> str:
    return f"{video_id}_{int(start_seconds)}_{comic_slug}{ext}"


def find_set_for_image(video_id: str, start_seconds: int):
    """Look up the Set a parsed image filename refers to.

    `start_seconds` from a filename is truncated to whole seconds, so match
    against the bucket it falls in rather than requiring exact equality.
    """
    from pipeline.models import Set

    return Set.objects.select_related("video", "comedian").get(
        video__video_id=video_id,
        start_seconds__gte=start_seconds,
        start_seconds__lt=start_seconds + 1,
    )


def rename_set_image(set_obj, *, new_comedian_slug: str | None = None) -> str | None:
    """Rename image files when a set's comedian slug changes.

    Renames in both the public media dir and the archive if the file exists
    in each. Updates nothing in the DB — callers must save the returned path.

    Returns the new media-relative path, or None if the set has no image or
    the image_url is already absolute (legacy rows we can't rename).
    """
    if not set_obj.image_url:
        return None
    if set_obj.image_url.startswith(("http://", "https://")):
        return None

    current_filename = Path(set_obj.image_url).name
    try:
        parsed = parse_image_name(Path(current_filename))
    except ValueError:
        return None

    ext = Path(current_filename).suffix
    slug = new_comedian_slug if new_comedian_slug is not None else parsed["comic_slug"]
    new_filename = image_filename(parsed["video_id"], set_obj.start_seconds, slug, ext)

    if new_filename == current_filename:
        return set_obj.image_url

    public_dir = settings.MEDIA_ROOT / "set-images"
    old_public = public_dir / current_filename
    if old_public.exists():
        old_public.rename(public_dir / new_filename)

    archive_dir = settings.PIPELINE_DATA_DIR / "set_images_archive"
    old_archive = archive_dir / current_filename
    if old_archive.exists():
        old_archive.rename(archive_dir / new_filename)

    return set_image_media_path(new_filename)

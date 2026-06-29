import re

from pipeline.models import Set


SET_SLUG_RE = re.compile(r"^(?P<video_id>[A-Za-z0-9_-]+)-set(?P<set_num>\d+)-(?P<comic>[a-z0-9][a-z0-9-]*)$")


def set_public_slug(set_obj: Set) -> str:
    return f"{set_obj.video.video_id}-set{set_obj.set_number:02d}-{set_obj.comedian.slug}"


def lookup_set_by_public_slug(slug: str):
    match = SET_SLUG_RE.fullmatch(slug)
    if not match:
        return Set.objects.none()

    return Set.objects.filter(
        video__video_id=match.group("video_id"),
        set_number=int(match.group("set_num")),
        comedian__slug=match.group("comic"),
    )

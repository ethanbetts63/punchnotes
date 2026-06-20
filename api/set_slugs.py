import re

from pipeline.models import Set


SET_SLUG_RE = re.compile(r"^kt(?P<episode>\d+)-set(?P<set>\d+)-(?P<comic>[a-z0-9-]+)$")


def set_public_slug(set_obj: Set) -> str:
    return f"kt{set_obj.video.number}-set{set_obj.set_number:02d}-{set_obj.comedian.slug}"


def lookup_set_by_public_slug(slug: str):
    match = SET_SLUG_RE.fullmatch(slug)
    if not match:
        return Set.objects.none()

    return Set.objects.filter(
        video__number=int(match.group("episode")),
        set_number=int(match.group("set")),
        comedian__slug=match.group("comic"),
    )

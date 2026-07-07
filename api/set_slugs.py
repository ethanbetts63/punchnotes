import re

from django.db.models import Q

from pipeline.models import Set


SET_SLUG_RE = re.compile(r"^(?P<video_id>[A-Za-z0-9_-]+)-(?P<start_seconds>\d+)-(?P<comic>[a-z0-9][a-z0-9-]*)$")


def set_public_slug(set_obj: Set) -> str:
    return f"{set_obj.video.video_id}-{int(set_obj.start_seconds)}-{set_obj.comedian.slug}"


def _parse_set_slug(slug: str) -> dict | None:
    match = SET_SLUG_RE.fullmatch(slug)
    if not match:
        return None
    start_seconds = int(match.group("start_seconds"))
    return {
        "video__video_id": match.group("video_id"),
        "start_seconds__gte": start_seconds,
        "start_seconds__lt": start_seconds + 1,
        "comedian__slug": match.group("comic"),
    }


def lookup_set_by_public_slug(slug: str):
    parsed = _parse_set_slug(slug)
    if not parsed:
        return Set.objects.none()

    return Set.objects.filter(**parsed)


def filter_sets_by_public_slugs(queryset, slugs):
    """Filter a Set queryset down to those matching any of the given public slugs."""
    parsed_slugs = [parsed for slug in slugs if (parsed := _parse_set_slug(slug))]
    if not parsed_slugs:
        return queryset.none()

    query = Q()
    for parsed in parsed_slugs:
        query |= Q(**parsed)
    return queryset.filter(query)

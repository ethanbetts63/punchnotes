import re

from django.utils.text import slugify

from pipeline.models import Video


VIDEO_SLUG_RE = re.compile(r"^.+--(?P<video_id>[A-Za-z0-9_-]+)$")


def video_public_slug(video: Video) -> str:
    title = slugify(video.title or f"kt-{video.number}" or video.video_id) or "episode"
    return f"{title}--{video.video_id}"


def lookup_video_by_public_slug(slug: str):
    match = VIDEO_SLUG_RE.fullmatch(slug)
    if not match:
        return Video.objects.none()
    return Video.objects.filter(video_id=match.group("video_id"))

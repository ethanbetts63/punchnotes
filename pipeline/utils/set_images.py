import re
from pathlib import Path

from django.conf import settings


IMAGE_NAME_RE = re.compile(
    r"^KT(?P<episode_number>\d+)_set(?P<set_number>\d+)_"
    r"(?P<comic_slug>[a-z0-9][a-z0-9_-]*)\.(?P<ext>jpe?g|png|webp)$",
    re.IGNORECASE,
)


def parse_image_name(path: Path) -> dict:
    match = IMAGE_NAME_RE.match(path.name)
    if not match:
        raise ValueError(
            f"Invalid image filename: {path.name}. Expected "
            "KT{episode}_set{number}_{slug}.jpg."
        )
    return {
        "episode_number": int(match.group("episode_number")),
        "set_number": int(match.group("set_number")),
        "comic_slug": match.group("comic_slug").lower().replace("_", "-"),
    }


def public_image_url(filename: str) -> str:
    base = settings.SERVER_BASE_URL.rstrip("/")
    return f"{base}/set-images/{filename}"

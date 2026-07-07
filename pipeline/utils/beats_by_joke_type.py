import json
import re

from django.core.management.base import CommandError

from pipeline.models import Beat, Comedian, Line

JOKE_TYPE_VALUES = {choice for choice, _ in Beat.JOKE_TYPE_CHOICES}
JOKE_BOOK_SIZES = {"small", "medium", "large"}

_TRAILING_DIGITS_RE = re.compile(r"(\d+)$")


def resolve_comedian(identifier: str) -> Comedian:
    slug_candidate = identifier.strip().lower().replace(" ", "-")
    comedian = Comedian.objects.filter(slug=slug_candidate).first()
    if comedian:
        return comedian

    comedian = Comedian.objects.filter(name__iexact=identifier.strip()).first()
    if comedian:
        return comedian

    raise CommandError(f"No comedian found matching {identifier!r}")


def normalize_joke_type(value: str) -> str:
    text = value.strip().lower().replace(" ", "-").replace("_", "-")
    if text in JOKE_TYPE_VALUES:
        return text
    if text.endswith("ies") and (text[:-3] + "y") in JOKE_TYPE_VALUES:
        return text[:-3] + "y"
    if text.endswith("s") and text[:-1] in JOKE_TYPE_VALUES:
        return text[:-1]

    allowed = ", ".join(sorted(JOKE_TYPE_VALUES))
    raise CommandError(f"--joke-type must be one of: {allowed}")


def normalize_joke_book(value: str) -> str:
    text = value.strip().lower()
    if text in JOKE_BOOK_SIZES:
        return text
    allowed = ", ".join(sorted(JOKE_BOOK_SIZES))
    raise CommandError(f"--joke-book must be one of: {allowed}")


def _ordinal(value: str) -> str:
    match = _TRAILING_DIGITS_RE.search(value)
    return match.group(1).zfill(3) if match else value


def build_beat_slug(beat: Beat) -> str:
    set_obj = beat.bit.set
    return (
        f"{set_obj.video.video_id}-{int(set_obj.start_seconds)}-{set_obj.comedian.slug}"
        f"?bit={_ordinal(beat.bit.bit_id)}&beat={_ordinal(beat.beat_id)}"
    )


def fetch_beats(joke_type: str, comedian: Comedian | None = None, joke_book: str | None = None):
    beats = Beat.objects.filter(joke_type=joke_type)
    if comedian is not None:
        beats = beats.filter(bit__set__comedian=comedian)
    if joke_book is not None:
        beats = beats.filter(bit__set__attributes__contains=[f"{joke_book}_joke_book"])
    return (
        beats.select_related("bit__set__video", "bit__set__comedian")
        .order_by("bit__set__comedian__slug", "bit__set__video__number", "bit__set__start_seconds", "bit__bit_id", "beat_id")
    )


def fetch_lines_for_beat(beat: Beat) -> list[str]:
    return list(
        Line.objects.filter(
            set_id=beat.bit.set_id,
            line_number__gte=beat.line_start,
            line_number__lte=beat.line_end,
        )
        .order_by("line_number")
        .values_list("text", flat=True)
    )


def build_report(joke_type: str, comedian: Comedian | None = None, joke_book: str | None = None) -> list[dict]:
    report = []
    for beat in fetch_beats(joke_type, comedian=comedian, joke_book=joke_book):
        report.append({
            "slug": build_beat_slug(beat),
            "comedian": beat.bit.set.comedian.name,
            "premise": beat.premise,
            "lines": fetch_lines_for_beat(beat),
        })
    return report


def render_txt(report: list[dict]) -> str:
    if not report:
        return ""
    blocks = ["\n".join([entry["slug"], *entry["lines"]]) for entry in report]
    return "\n\n".join(blocks) + "\n"


def render_json(joke_type: str, report: list[dict], comedian: Comedian | None = None, joke_book: str | None = None) -> str:
    payload = {
        "comedian": comedian.name if comedian else None,
        "joke_book": joke_book,
        "joke_type": joke_type,
        "count": len(report),
        "beats": report,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)

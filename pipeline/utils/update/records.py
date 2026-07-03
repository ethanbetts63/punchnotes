from collections import defaultdict

from django.db.models import Avg, Count, Q

from pipeline.json_validation.constants import JOKE_TYPE_FIELDS, OPTIONAL_JOKE_TYPE_FIELDS
from pipeline.utils.ownership import infer_line_ownership
from pipeline.utils.beat_search import build_beat_search_text
from pipeline.utils.known_comedians import normalize_known_appearance_attributes
from pipeline.utils.set_images import rename_set_image
from pipeline.models import Beat, Bit, Comedian, Video, Line, Set


def get_video_for_set(video_id: str) -> Video:
    try:
        return Video.objects.get(video_id=video_id)
    except Video.DoesNotExist as exc:
        raise ValueError(
            f"Video {video_id} is not in the database. Run update --ep_meta before importing annotated sets."
        ) from exc


def merge_attributes(existing: list, incoming: list) -> list:
    return list(dict.fromkeys(v for v in [*existing, *incoming] if v))


def meta_attributes(meta: dict) -> list:
    return list(meta.get("comedian_attributes", []))


def upsert_comedian(slug: str, meta: dict) -> Comedian:
    comedian, _ = Comedian.objects.get_or_create(
        slug=slug,
        defaults={
            "name": meta["comedian_name"],
        },
    )
    incoming_attributes = meta_attributes(meta)
    merged_attributes = merge_attributes(comedian.attributes, incoming_attributes)
    merged_attributes = normalize_known_appearance_attributes(slug, merged_attributes)
    update_fields = []
    if merged_attributes != comedian.attributes:
        comedian.attributes = merged_attributes
        update_fields.append("attributes")
    if update_fields:
        comedian.save(update_fields=update_fields)
    return comedian


def _apply_set_number(set_obj, new_number: int) -> None:
    if set_obj.set_number == new_number:
        return
    update_fields = ["set_number"]
    new_image_url = rename_set_image(set_obj, new_number)
    if new_image_url is not None and new_image_url != set_obj.image_url:
        set_obj.image_url = new_image_url
        update_fields.append("image_url")
    set_obj.set_number = new_number
    set_obj.save(update_fields=update_fields)


def resequence_video_sets(video: Video) -> None:
    """Assign 1-indexed set numbers by source start time."""
    sets = list(video.sets.order_by("start_seconds", "id"))
    if not sets:
        return

    max_set_number = max(set_obj.set_number for set_obj in sets)
    offset = max_set_number + len(sets) + 1
    for i, set_obj in enumerate(sets, start=1):
        _apply_set_number(set_obj, offset + i)

    for i, set_obj in enumerate(sets, start=1):
        _apply_set_number(set_obj, i)


def upsert_set(video: Video, comedian: Comedian, meta: dict) -> Set:
    start_seconds = meta["start_seconds"]
    set_attributes = list(meta.get("set_attributes", []))
    fields = {
        "comedian": comedian,
        "start_seconds": start_seconds,
        "interview_end_line": meta.get("interview_end_line"),
        "interview_end_seconds": meta.get("interview_end_seconds"),
        "attributes": set_attributes,
    }

    set_obj = video.sets.filter(start_seconds=start_seconds).first()
    if set_obj is None:
        last_set_number = video.sets.order_by("-set_number").values_list("set_number", flat=True).first()
        set_obj = Set.objects.create(video=video, set_number=(last_set_number or 0) + 1, **fields)
    else:
        for k, v in fields.items():
            setattr(set_obj, k, v)
        set_obj.save(update_fields=list(fields.keys()))

    resequence_video_sets(video)
    set_obj.refresh_from_db()
    return set_obj


def refresh_set_ratios(set_obj: Set) -> None:
    counts = set_obj.lines.aggregate(
        punchlines=Count('id', filter=Q(label='punchline')),
        tags=Count('id', filter=Q(label='tag')),
        setups=Count('id', filter=Q(label='setup')),
        fluffs=Count('id', filter=Q(label='fluff')),
    )
    p, t, s, f = counts['punchlines'], counts['tags'], counts['setups'], counts['fluffs']
    denominator = s + f
    set_obj.punch_density = (p + t) / denominator if denominator > 0 else None
    set_obj.tag_density = t / p if p > 0 else None
    set_obj.save(update_fields=['punch_density', 'tag_density'])


def refresh_comedian_stats(comedian: Comedian) -> None:
    sets = comedian.sets.annotate(
        n_bits=Count('bits', distinct=True),
        n_beats=Count('bits__beats', distinct=True),
    )
    agg = sets.aggregate(
        avg_punch_density=Avg('punch_density'),
        avg_tag_density=Avg('tag_density'),
        avg_bits=Avg('n_bits'),
        avg_beats=Avg('n_beats'),
    )
    comedian.set_count = comedian.sets.values('video_id').distinct().count()
    comedian.joke_count = Bit.objects.filter(set__comedian=comedian).count()
    comedian.avg_punch_density = agg['avg_punch_density']
    comedian.avg_tag_density = agg['avg_tag_density']
    comedian.avg_bits_per_set = agg['avg_bits']
    comedian.avg_beats_per_set = agg['avg_beats']
    comedian.has_small_joke_book = sets.filter(attributes__contains=['small_joke_book']).exists()
    comedian.has_medium_joke_book = sets.filter(attributes__contains=['medium_joke_book']).exists()
    comedian.has_large_joke_book = sets.filter(attributes__contains=['large_joke_book']).exists()
    comedian.save(update_fields=[
        'set_count', 'joke_count', 'avg_punch_density', 'avg_tag_density',
        'avg_bits_per_set', 'avg_beats_per_set',
        'has_small_joke_book', 'has_medium_joke_book', 'has_large_joke_book',
    ])


def refresh_comedian_image(comedian: Comedian) -> None:
    latest = (
        comedian.sets
        .exclude(image_url__isnull=True)
        .exclude(image_url="")
        .select_related("video")
        .order_by("-video__number", "-start_seconds", "-id")
        .first()
    )
    image_url = latest.image_url if latest else None
    image_set_id = latest.id if latest else None
    if comedian.image_url == image_url and comedian.image_set_id == image_set_id:
        return
    comedian.image_url = image_url
    comedian.image_set_id = image_set_id
    comedian.save(update_fields=["image_url", "image_set"])


def import_lines(set_obj: Set, lines_data: list) -> list:
    deleted, _ = set_obj.lines.all().delete()
    lines = [
        Line(
            set=set_obj,
            line_number=line["line_number"],
            label=line["label"],
            text=line["text"],
            start_seconds=line["start"],
        )
        for line in lines_data
    ]
    Line.objects.bulk_create(lines)
    refresh_set_ratios(set_obj)
    return lines


def _bit_ratios(label_by_line: dict, line_numbers: set) -> tuple[float | None, float | None]:
    counts: dict[str, int] = {}
    for ln in line_numbers:
        label = label_by_line.get(ln)
        if label:
            counts[label] = counts.get(label, 0) + 1
    p = counts.get("punchline", 0)
    t = counts.get("tag", 0)
    s = counts.get("setup", 0)
    f = counts.get("fluff", 0)
    denominator = s + f
    return (p + t) / denominator if denominator > 0 else None, t / p if p > 0 else None


def _extract_joke_fields(beat_data: dict) -> dict:
    joke_type = beat_data.get("joke_type") or ""
    fields = (*JOKE_TYPE_FIELDS.get(joke_type, ()), *OPTIONAL_JOKE_TYPE_FIELDS.get(joke_type, ()))
    return {f: beat_data[f] for f in fields if f in beat_data}


def import_bits(set_obj: Set, lines_data: list, bit_meta: dict) -> None:
    set_obj.bits.all().delete()

    label_by_line = {line["line_number"]: line["label"] for line in lines_data}
    ownership = infer_line_ownership(lines_data)
    bit_lines: dict[int, list] = defaultdict(list)
    beat_lines: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    for line in lines_data:
        b, bt = ownership[int(line["line_number"])]
        if b is not None:
            bit_lines[b].append(line["line_number"])
            if bt is not None:
                beat_lines[b][bt].append(line["line_number"])

    bit_count = 0
    beats_to_create = []
    for bit_num_str, bit_data in bit_meta.items():
        bit_num = int(bit_num_str)
        lns = bit_lines.get(bit_num, [])
        if not lns:
            continue
        punch_density, tag_density = _bit_ratios(label_by_line, set(lns))
        bit = Bit.objects.create(
            set=set_obj,
            bit_id=f"bit_{bit_num:03d}",
            line_start=min(lns),
            line_end=max(lns),
            punch_density=punch_density,
            tag_density=tag_density,
        )
        bit_count += 1
        for beat_num_str, beat_data in bit_data.get("beats", {}).items():
            beat_num = int(beat_num_str)
            blns = beat_lines[bit_num].get(beat_num, [])
            if not blns:
                continue
            beats_to_create.append(Beat(
                bit=bit,
                beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
                line_start=min(blns),
                line_end=max(blns),
                premise=beat_data.get("premise"),
                joke_type=beat_data.get("joke_type"),
                joke_fields=_extract_joke_fields(beat_data),
                search_text=build_beat_search_text(lines_data, set(blns)),
            ))

    Beat.objects.bulk_create(beats_to_create)

    set_obj.bit_count = bit_count
    set_obj.save(update_fields=["bit_count"])


def refresh_video_counts(video: Video) -> None:
    """Recompute denormalised counts from the video's current sets."""
    sets = list(video.sets.select_related("comedian").all())
    video.set_count = len(sets)
    video.bucket_pull_count = sum(1 for s in sets if "bucket_pull" in s.comedian.attributes)
    video.golden_ticket_count = sum(1 for s in sets if "golden_ticket" in s.comedian.attributes)
    video.regular_count = sum(1 for s in sets if "regular" in s.comedian.attributes)
    video.large_joke_book_count = sum(1 for s in sets if "large_joke_book" in s.attributes)
    video.save(update_fields=[
        "set_count", "bucket_pull_count", "golden_ticket_count",
        "regular_count", "large_joke_book_count",
    ])

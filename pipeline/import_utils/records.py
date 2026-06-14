import re
from collections import defaultdict

from django.db.models import Avg, Count, Q

from pipeline.import_utils.ownership import infer_line_ownership
from pipeline.models import Beat, Bit, Comedian, Video, Line, Set
from pipeline.import_utils.known_comedians import normalize_known_appearance_attributes


def parse_episode_number(title: str) -> int | None:
    m = re.search(r"#(\d+)", title)
    return int(m.group(1)) if m else None


def upsert_episode(video_id: str, meta: dict) -> Video:
    video, _ = Video.objects.get_or_create(
        video_id=video_id,
        defaults={
            "number": parse_episode_number(meta["episode_title"]),
            "title": meta["episode_title"],
            "url": meta["episode_url"],
            "date": meta.get("publish_date"),
        },
    )
    update_fields = []
    if video.number is None:
        video.number = parse_episode_number(video.title)
        update_fields.append("number")
    if video.date is None and meta.get("publish_date"):
        video.date = meta["publish_date"]
        update_fields.append("date")
    if update_fields:
        video.save(update_fields=update_fields)
    return video


def merge_attributes(existing, incoming):
    merged = []
    seen = set()
    for value in [*(existing or []), *(incoming or [])]:
        if value and value not in seen:
            merged.append(value)
            seen.add(value)
    return merged


def meta_attributes(meta):
    return list(meta.get("comedian_attributes") or [])


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


def resequence_episode_sets(video: Video) -> None:
    """Assign 1-indexed set numbers by source start time."""
    sets = list(video.sets.order_by("start_seconds", "id"))
    if not sets:
        return

    max_set_number = max(set_obj.set_number for set_obj in sets)
    offset = max_set_number + len(sets) + 1
    for i, set_obj in enumerate(sets, start=1):
        if set_obj.set_number != offset + i:
            set_obj.set_number = offset + i
            set_obj.save(update_fields=["set_number"])

    for i, set_obj in enumerate(sets, start=1):
        if set_obj.set_number != i:
            set_obj.set_number = i
            set_obj.save(update_fields=["set_number"])


def upsert_set(video: Video, comedian: Comedian, meta: dict) -> Set:
    start_seconds = meta["start_seconds"]
    set_obj = video.sets.filter(start_seconds=start_seconds).first()
    set_attributes = list(meta.get("set_attributes") or [])
    if set_obj is None:
        last_set_number = video.sets.order_by("-set_number").values_list("set_number", flat=True).first()
        next_set_number = (last_set_number or 0) + 1
        set_obj = Set.objects.create(
            video=video,
            set_number=next_set_number,
            comedian=comedian,
            start_seconds=start_seconds,
            interview_end_line=meta.get("interview_end_line"),
            interview_end_seconds=meta.get("interview_end_seconds"),
            attributes=set_attributes,
        )
    set_obj.comedian = comedian
    set_obj.start_seconds = start_seconds
    set_obj.interview_end_line = meta.get("interview_end_line")
    set_obj.interview_end_seconds = meta.get("interview_end_seconds")
    set_obj.attributes = set_attributes
    set_obj.save(update_fields=[
        "comedian", "start_seconds", "interview_end_line",
        "interview_end_seconds", "attributes",
    ])
    resequence_episode_sets(video)
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
    set_obj.hit_ratio = (p + t) / denominator if denominator > 0 else None
    set_obj.punchline_tag_ratio = p / t if t > 0 else None
    set_obj.save(update_fields=['hit_ratio', 'punchline_tag_ratio'])


def refresh_comedian_stats(comedian: Comedian) -> None:
    sets = comedian.sets.annotate(
        n_bits=Count('bits', distinct=True),
        n_beats=Count('bits__beats', distinct=True),
    )
    agg = sets.aggregate(
        avg_hit=Avg('hit_ratio'),
        avg_pt=Avg('punchline_tag_ratio'),
        avg_bits=Avg('n_bits'),
        avg_beats=Avg('n_beats'),
    )
    comedian.set_count = comedian.sets.values('video_id').distinct().count()
    comedian.joke_count = Bit.objects.filter(set__comedian=comedian).count()
    comedian.avg_hit_ratio = agg['avg_hit']
    comedian.avg_punchline_tag_ratio = agg['avg_pt']
    comedian.avg_bits_per_set = agg['avg_bits']
    comedian.avg_beats_per_set = agg['avg_beats']
    comedian.has_small_joke_book = sets.filter(attributes__contains=['small_joke_book']).exists()
    comedian.has_medium_joke_book = sets.filter(attributes__contains=['medium_joke_book']).exists()
    comedian.has_large_joke_book = sets.filter(attributes__contains=['large_joke_book']).exists()
    comedian.save(update_fields=[
        'set_count', 'joke_count', 'avg_hit_ratio', 'avg_punchline_tag_ratio',
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
    refresh_comedian_stats(set_obj.comedian)
    return lines


def _bit_ratios(lines_data: list, line_numbers: set) -> tuple[float | None, float | None]:
    """Compute hit_ratio and punchline_tag_ratio for a subset of lines."""
    counts: dict[str, int] = {"setup": 0, "punchline": 0, "tag": 0, "fluff": 0}
    for line in lines_data:
        if line["line_number"] in line_numbers:
            counts[line["label"]] = counts.get(line["label"], 0) + 1
    p, t, s, f = counts["punchline"], counts["tag"], counts["setup"], counts["fluff"]
    denominator = s + f
    hit_ratio = (p + t) / denominator if denominator > 0 else None
    punchline_tag_ratio = p / t if t > 0 else None
    return hit_ratio, punchline_tag_ratio


_infer_line_ownership = infer_line_ownership


JOKE_TYPE_FIELDS = {
    "misdirect":           ["bait", "implication", "reveal"],
    "reframe":             ["subject", "reframe"],
    "phonetic-match":      ["heard", "reheard", "reason"],
    "double-meaning":      ["phrase", "expected", "comic"],
    "contradiction":       ["subject", "a", "b"],
    "analogy":             ["a", "b", "shared"],
    "hyperbole":           ["subject", "extreme"],
    "elephant-in-the-room": ["elephant"],
    "anti-humor":          ["frame", "answer"],
}


def _extract_joke_fields(beat_data: dict) -> dict:
    joke_type = beat_data.get("joke_type") or ""
    fields = JOKE_TYPE_FIELDS.get(joke_type, [])
    return {f: beat_data[f] for f in fields if f in beat_data}


def import_bits(set_obj: Set, lines_data: list, bit_meta: dict) -> None:
    set_obj.bits.all().delete()

    ownership = _infer_line_ownership(lines_data)
    bit_lines: dict[int, list] = defaultdict(list)
    beat_lines: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    for line in lines_data:
        b, bt = ownership[int(line["line_number"])]
        if b is not None:
            bit_lines[b].append(line["line_number"])
            if bt is not None:
                beat_lines[b][bt].append(line["line_number"])

    for bit_num_str, bit_data in bit_meta.items():
        bit_num = int(bit_num_str)
        lns = bit_lines.get(bit_num, [])
        if not lns:
            continue
        hit_ratio, punchline_tag_ratio = _bit_ratios(lines_data, set(lns))
        bit = Bit.objects.create(
            set=set_obj,
            bit_id=f"bit_{bit_num:03d}",
            summary=bit_data.get("summary"),
            line_start=min(lns),
            line_end=max(lns),
            hit_ratio=hit_ratio,
            punchline_tag_ratio=punchline_tag_ratio,
        )
        for beat_num_str, beat_data in bit_data.get("beats", {}).items():
            beat_num = int(beat_num_str)
            blns = beat_lines[bit_num].get(beat_num, [])
            if not blns:
                continue
            Beat.objects.create(
                bit=bit,
                beat_id=f"bit_{bit_num:03d}_beat_{beat_num:03d}",
                line_start=min(blns),
                line_end=max(blns),
                premise=beat_data.get("premise"),
                joke_type=beat_data.get("joke_type") or None,
                joke_fields=_extract_joke_fields(beat_data),
            )

    set_obj.bit_count = set_obj.bits.count()
    set_obj.save(update_fields=["bit_count"])
    refresh_comedian_stats(set_obj.comedian)


def refresh_episode_counts(video: Video) -> None:
    """Recompute denormalised counts from the video's current sets."""
    sets = list(video.sets.select_related("comedian").all())
    video.set_count = len(sets)
    video.bucket_pull_count = sum(1 for s in sets if "bucket_pull" in (s.comedian.attributes or []))
    video.golden_ticket_count = sum(1 for s in sets if "golden_ticket" in (s.comedian.attributes or []))
    video.regular_count = sum(1 for s in sets if "regular" in (s.comedian.attributes or []))
    video.large_joke_book_count = sum(1 for s in sets if "large_joke_book" in (s.attributes or []))
    video.save(update_fields=[
        "set_count", "bucket_pull_count", "golden_ticket_count",
        "regular_count", "large_joke_book_count",
    ])

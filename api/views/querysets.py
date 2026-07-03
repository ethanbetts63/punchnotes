from django.db.models import Exists, F, OuterRef, Prefetch, Q

from api.set_slugs import filter_sets_by_public_slugs
from pipeline.models import Beat, Bit, Comedian, Video, Set


COMEDIAN_SORT_FIELDS = {
    "set_count": "set_count",
    "avg_punch_density": "avg_punch_density",
    "avg_tag_density": "avg_tag_density",
    "avg_bits_per_set": "avg_bits_per_set",
    "avg_beats_per_set": "avg_beats_per_set",
}

VIDEO_SORT_FIELDS = {
    "date": "date",
    "duration": "duration_seconds",
    "set_count": "set_count",
    "bucket_pulls": "bucket_pull_count",
    "golden_tickets": "golden_ticket_count",
    "large_joke_books": "large_joke_book_count",
    "regulars": "regular_count",
    "view_count": "view_count",
    "like_count": "like_count",
    "like_ratio": "view_like_ratio",
}

SET_SORT_FIELDS = {
    "bit_count": "bit_count",
    "punch_density": "punch_density",
    "tag_density": "tag_density",
}

BIT_SORT_FIELDS = {
    "punch_density": "punch_density",
    "tag_density": "tag_density",
}


def nullable_order(field, asc=False):
    return F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)


def build_comedian_list_queryset(params):
    comedians = Comedian.objects.annotate(
        has_sets=Exists(Set.objects.filter(comedian_id=OuterRef("pk")))
    ).filter(has_sets=True)

    q = (params.get("q") or "").strip()
    if q:
        comedians = comedians.filter(name__icontains=q)

    attribute = (params.get("attribute") or "").strip()
    if attribute:
        comedians = comedians.filter(attributes__contains=[attribute])

    joke_book = (params.get("joke_book") or "").strip()
    if joke_book == "small":
        comedians = comedians.filter(has_small_joke_book=True)
    elif joke_book == "medium":
        comedians = comedians.filter(has_medium_joke_book=True)
    elif joke_book == "large":
        comedians = comedians.filter(has_large_joke_book=True)

    sort_key = (params.get("sort") or "").strip()
    field = COMEDIAN_SORT_FIELDS.get(sort_key)
    if field:
        comedians = comedians.order_by(nullable_order(field, params.get("asc") == "1"), "name")
    else:
        comedians = comedians.order_by("name")

    return comedians


def build_video_list_queryset(params):
    videos = Video.objects.all()

    q = (params.get("q") or "").strip()
    if q:
        number = q.upper().removeprefix("KT").strip().removeprefix("#").strip()
        filters = Q(title__icontains=q)
        if number.isdigit():
            filters |= Q(number=int(number))
        videos = videos.filter(filters)

    has = (params.get("has") or "").strip()
    if has == "bucket_pull":
        videos = videos.filter(bucket_pull_count__gt=0)
    elif has == "golden_ticket":
        videos = videos.filter(golden_ticket_count__gt=0)
    elif has == "regular":
        videos = videos.filter(regular_count__gt=0)
    elif has == "large_joke_book":
        videos = videos.filter(large_joke_book_count__gt=0)

    sort_key = (params.get("sort") or "date").strip()
    field = VIDEO_SORT_FIELDS.get(sort_key, "date")
    return videos.order_by(nullable_order(field, params.get("asc") == "1"), "-number")


def build_set_list_queryset(params):
    sets = Set.objects.select_related("comedian", "video")

    slugs_raw = (params.get("slugs") or "").strip()
    if slugs_raw:
        slugs = [s.strip() for s in slugs_raw.split(",") if s.strip()]
        sets = filter_sets_by_public_slugs(sets, slugs)

    q = (params.get("q") or "").strip()
    if q:
        sets = sets.filter(comedian__name__icontains=q)

    attribute = (params.get("attribute") or "").strip()
    if attribute:
        sets = sets.filter(comedian__attributes__contains=[attribute])

    joke_book = (params.get("joke_book") or "").strip()
    if joke_book in ("small", "medium", "large"):
        sets = sets.filter(attributes__contains=[f"{joke_book}_joke_book"])

    sort_key = (params.get("sort") or "").strip()
    field = SET_SORT_FIELDS.get(sort_key)
    if field:
        sets = sets.order_by(nullable_order(field, params.get("asc") == "1"))
    else:
        sets = sets.order_by("-video__number", "start_seconds")

    return sets


def build_bit_list_queryset(params):
    bits = (
        Bit.objects.select_related("set__comedian", "set__video")
        .prefetch_related("beats")
        .filter(beats__isnull=False)
        .distinct()
    )

    joke_type = params.get("joke_type")
    if joke_type:
        bits = bits.filter(beats__joke_type=joke_type)

    q = (params.get("q") or "").strip()
    if q:
        bits = bits.filter(
            Q(beats__premise__icontains=q)
            | Q(beats__joke_type__icontains=q)
            | Q(set__comedian__name__icontains=q)
            | Q(set__video__title__icontains=q)
        ).distinct()

    sort_key = (params.get("sort") or "").strip()
    field = BIT_SORT_FIELDS.get(sort_key)
    if field:
        bits = bits.order_by(nullable_order(field, params.get("asc") == "1"))

    return bits


def build_beat_search_queryset(params):
    beats = (
        Beat.objects.select_related("bit__set__comedian", "bit__set__video")
        .prefetch_related("bit__set__lines")
        .filter(joke_type__isnull=False)
        .exclude(joke_type="")
    )

    beat_ids_raw = (params.get("beat_ids") or "").strip()
    if beat_ids_raw:
        beat_ids = [b.strip() for b in beat_ids_raw.split(",") if b.strip()]
        beats = beats.filter(beat_id__in=beat_ids)

    joke_type = (params.get("joke_type") or "").strip()
    if joke_type:
        beats = beats.filter(joke_type=joke_type)

    q = (params.get("q") or "").strip()
    if q:
        beats = beats.filter(search_text__icontains=q)

    return beats


def build_comedian_detail_queryset():
    return Comedian.objects.prefetch_related(
        Prefetch(
            "sets",
            queryset=Set.objects.select_related("video", "comedian").order_by("-video__number"),
        )
    )

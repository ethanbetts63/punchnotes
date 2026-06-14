from django.db.models import Exists, F, OuterRef, Prefetch, Q

from pipeline.models import Beat, Bit, Comedian, Video, Line, Set


COMEDIAN_SORT_FIELDS = {
    "set_count": "set_count",
    "avg_hit_ratio": "avg_hit_ratio",
    "avg_punchline_tag_ratio": "avg_punchline_tag_ratio",
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
    "hit_ratio": "hit_ratio",
    "punchline_tag_ratio": "punchline_tag_ratio",
}

BIT_SORT_FIELDS = {
    "hit_ratio": "hit_ratio",
    "punchline_tag_ratio": "punchline_tag_ratio",
}

SEARCHABLE_BEAT_LINE_LABELS = ("setup", "punchline", "tag")


def build_comedian_list_queryset(params):
    comedians = Comedian.objects.all()

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
        asc = params.get("asc") == "1"
        order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
        comedians = comedians.order_by(order, "name")
    else:
        comedians = comedians.order_by("name")

    return comedians


def build_video_list_queryset(params):
    videos = Video.objects.prefetch_related("guests")

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
    asc = params.get("asc") == "1"
    order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
    return videos.order_by(order, "-number")


def build_set_list_queryset(params):
    sets = Set.objects.select_related("comedian", "video")

    q = (params.get("q") or "").strip()
    if q:
        sets = sets.filter(Q(comedian__name__icontains=q) | Q(video__title__icontains=q))

    attribute = (params.get("attribute") or "").strip()
    if attribute:
        sets = sets.filter(comedian__attributes__contains=[attribute])

    joke_book = (params.get("joke_book") or "").strip()
    if joke_book in ("small", "medium", "large"):
        sets = sets.filter(attributes__contains=[f"{joke_book}_joke_book"])

    sort_key = (params.get("sort") or "").strip()
    field = SET_SORT_FIELDS.get(sort_key)
    if field:
        asc = params.get("asc") == "1"
        order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
        sets = sets.order_by(order)
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
            Q(summary__icontains=q)
            | Q(beats__premise__icontains=q)
            | Q(beats__joke_type__icontains=q)
            | Q(set__comedian__name__icontains=q)
            | Q(set__video__title__icontains=q)
        ).distinct()

    sort_key = (params.get("sort") or "").strip()
    field = BIT_SORT_FIELDS.get(sort_key)
    if field:
        asc = params.get("asc") == "1"
        order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
        bits = bits.order_by(order)

    return bits


def build_beat_search_queryset(params):
    beats = (
        Beat.objects.select_related("bit__set__comedian", "bit__set__video")
        .prefetch_related("bit__set__lines")
        .filter(joke_type__isnull=False)
        .exclude(joke_type="")
    )

    joke_type = (params.get("joke_type") or "").strip()
    if joke_type:
        beats = beats.filter(joke_type=joke_type)

    q = (params.get("q") or "").strip()
    if q:
        matching_lines = Line.objects.filter(
            set_id=OuterRef("bit__set_id"),
            line_number__gte=OuterRef("line_start"),
            line_number__lte=OuterRef("line_end"),
            label__in=SEARCHABLE_BEAT_LINE_LABELS,
            text__icontains=q,
        )
        beats = beats.annotate(has_matching_line=Exists(matching_lines)).filter(has_matching_line=True)

    return beats


def build_comedian_detail_queryset():
    return Comedian.objects.prefetch_related(
        Prefetch(
            "sets",
            queryset=Set.objects.select_related("video").order_by("-video__number"),
        )
    )

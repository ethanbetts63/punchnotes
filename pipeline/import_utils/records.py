import re
from collections import defaultdict

from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


def parse_episode_number(title: str) -> int | None:
    m = re.search(r"#(\d+)", title)
    return int(m.group(1)) if m else None


def upsert_episode(video_id: str, meta: dict) -> Episode:
    episode, _ = Episode.objects.get_or_create(
        video_id=video_id,
        defaults={
            "episode_number": parse_episode_number(meta["episode_title"]),
            "episode_title": meta["episode_title"],
            "episode_url": meta["episode_url"],
            "published_at": meta.get("publish_date"),
        },
    )
    update_fields = []
    if episode.episode_number is None:
        episode.episode_number = parse_episode_number(episode.episode_title)
        update_fields.append("episode_number")
    if episode.published_at is None and meta.get("publish_date"):
        episode.published_at = meta["publish_date"]
        update_fields.append("published_at")
    if update_fields:
        episode.save(update_fields=update_fields)
    return episode


def upsert_comedian(slug: str, meta: dict) -> Comedian:
    comedian, _ = Comedian.objects.get_or_create(
        slug=slug,
        defaults={
            "name": meta["comedian_name"],
            "comedian_type": meta["comedian_type"],
        },
    )
    return comedian


def upsert_set(episode: Episode, set_number: int, comedian: Comedian, meta: dict) -> Set:
    set_obj, _ = Set.objects.get_or_create(
        episode=episode,
        set_number=set_number,
        defaults={
            "comedian": comedian,
            "start_seconds": meta["start_seconds"],
            "interview_end_line": meta.get("interview_end_line"),
            "interview_end_seconds": meta.get("interview_end_seconds"),
            "joke_book": meta.get("joke_book"),
        },
    )
    set_obj.comedian = comedian
    set_obj.start_seconds = meta["start_seconds"]
    set_obj.interview_end_line = meta.get("interview_end_line")
    set_obj.interview_end_seconds = meta.get("interview_end_seconds")
    set_obj.joke_book = meta.get("joke_book")
    set_obj.save(update_fields=[
        "comedian", "start_seconds", "interview_end_line",
        "interview_end_seconds", "joke_book",
    ])
    return set_obj


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
    return lines


def import_bits(set_obj: Set, lines_data: list, bit_meta: dict) -> None:
    set_obj.bits.all().delete()

    bit_lines: dict[int, list] = defaultdict(list)
    beat_lines: dict[int, dict] = defaultdict(lambda: defaultdict(list))
    for line in lines_data:
        b = line.get("bit")
        bt = line.get("beat")
        if b is not None:
            bit_lines[b].append(line["line_number"])
            if bt is not None:
                beat_lines[b][bt].append(line["line_number"])

    for bit_num_str, bit_data in bit_meta.items():
        bit_num = int(bit_num_str)
        lns = bit_lines.get(bit_num, [])
        if not lns:
            continue
        bit = Bit.objects.create(
            set=set_obj,
            bit_id=f"bit_{bit_num:03d}",
            premise=bit_data.get("premise"),
            line_start=min(lns),
            line_end=max(lns),
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
                topics=beat_data.get("topics", []),
            )


def refresh_episode_counts(episode: Episode) -> None:
    """Recompute denormalised counts from the episode's current sets."""
    sets = list(episode.sets.select_related("comedian").all())
    episode.bucket_pull_count = sum(1 for s in sets if s.comedian.comedian_type == "bucket_pull")
    episode.golden_ticket_count = sum(1 for s in sets if s.comedian.comedian_type == "golden_ticket")
    episode.regular_count = sum(1 for s in sets if s.comedian.comedian_type == "regular")
    episode.large_joke_book_count = sum(1 for s in sets if s.joke_book == "large")
    episode.save(update_fields=[
        "bucket_pull_count", "golden_ticket_count",
        "regular_count", "large_joke_book_count",
    ])

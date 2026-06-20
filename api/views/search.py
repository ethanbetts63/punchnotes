from rest_framework.response import Response
from rest_framework.views import APIView

from api.beat_utils import describe_beat_lines
from api.serializers.fields import absolute_media_url
from api.set_slugs import set_public_slug
from api.video_slugs import video_public_slug
from .querysets import (
    build_beat_search_queryset,
    build_comedian_list_queryset,
    build_video_list_queryset,
    build_set_list_queryset,
)


GROUP_LIMIT = 8


def text_score(query: str, *values: str | None) -> int:
    q = query.lower()
    best = 0
    for value in values:
        if not value:
            continue
        text = value.lower()
        if text == q:
            best = max(best, 100)
        elif text.startswith(q):
            best = max(best, 80)
        elif q in text:
            best = max(best, 50)
    return best


def result(type_, title, subtitle, href, meta=None, score=0, **extra):
    return {
        "type": type_,
        "title": title,
        "subtitle": subtitle,
        "href": href,
        "meta": meta or [],
        "score": score,
        **extra,
    }


def fmt_count(value, singular, plural=None):
    plural = plural or f"{singular}s"
    return f"{value} {singular if value == 1 else plural}"


def compact_ordinal_id(value: str) -> str:
    suffix = ""
    for char in reversed(value):
        if not char.isdigit():
            break
        suffix = char + suffix
    return suffix.zfill(3) if suffix else value


class NavSearchView(APIView):
    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            empty = {
                "query": "",
                "top_result": None,
                "comedians": [],
                "episodes": [],
                "sets": [],
                "beats": [],
            }
            return Response(empty)

        comedians = self.search_comedians(query)
        episodes = self.search_episodes(query)
        sets = self.search_sets(query)
        beats = self.search_beats(query)
        all_results = comedians + episodes + sets + beats
        top_result = max(all_results, key=lambda item: item["score"], default=None)

        return Response({
            "query": query,
            "top_result": top_result,
            "comedians": comedians,
            "episodes": episodes,
            "sets": sets,
            "beats": beats,
        })

    def search_comedians(self, query):
        rows = build_comedian_list_queryset({"q": query})
        results = []
        for comedian in rows[:GROUP_LIMIT]:
            meta = [
                fmt_count(comedian.set_count, "set"),
            ]
            if comedian.has_large_joke_book:
                meta.append("big joke book")
            score = text_score(query, comedian.name, comedian.slug) + min(comedian.set_count, 20)
            results.append(result(
                "comedian",
                comedian.name,
                "Comedian",
                f"/killtony/comedians/{comedian.slug}",
                meta,
                score,
                image_url=absolute_media_url(comedian.image_url, self.request),
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_episodes(self, query):
        rows = build_video_list_queryset({"q": query})
        results = []
        for episode in rows[:GROUP_LIMIT]:
            meta = [
                fmt_count(episode.set_count, "set"),
            ]
            if episode.date:
                meta.append(episode.date.isoformat())
            if episode.view_count is not None:
                meta.append(f"{episode.view_count:,} views")
            score = text_score(query, episode.title, str(episode.number or ""))
            score += min((episode.view_count or 0) // 100_000, 20)
            results.append(result(
                "episode",
                episode.title,
                "Episode",
                f"/killtony/episodes/{video_public_slug(episode)}",
                meta,
                score,
                youtube_id=episode.video_id,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_sets(self, query):
        rows = build_set_list_queryset({"q": query})
        results = []
        for set_obj in rows[:GROUP_LIMIT]:
            title = f"{set_obj.comedian.name} - KT #{set_obj.video.number}"
            meta = [
                f"Set {set_obj.set_number}",
                fmt_count(set_obj.bit_count, "bit"),
            ]
            attrs = set_obj.attributes or []
            joke_book_sizes = [a.removesuffix("_joke_book") for a in attrs if a.endswith("_joke_book")]
            for size in joke_book_sizes:
                meta.append(f"{size} joke book")
            score = text_score(query, set_obj.comedian.name)
            if "large_joke_book" in attrs:
                score += 10
            results.append(result(
                "set",
                title,
                set_obj.video.title,
                f"/killtony/sets/{set_public_slug(set_obj)}",
                meta,
                score,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_beats(self, query):
        rows = build_beat_search_queryset({"q": query})
        beat_results = []
        for beat in rows[:GROUP_LIMIT]:
            beat_data = describe_beat_lines(beat, query=query)
            match = beat_data["matched_line"]
            punchline = beat_data["punchline"]
            title = match.text if match else punchline or f"{beat.joke_type} beat"
            meta = []
            if match:
                meta.append(match.label)
            if beat.joke_type:
                meta.append(beat.joke_type)
            score = text_score(query, match.text if match else "", punchline)
            if match and match.label == "punchline":
                score += 5
            beat_results.append(result(
                "beat",
                title,
                f"{beat.bit.set.comedian.name} - KT #{beat.bit.set.video.number}",
                (
                    f"/killtony/sets/{set_public_slug(beat.bit.set)}"
                    f"?bit={compact_ordinal_id(beat.bit.bit_id)}&beat={compact_ordinal_id(beat.beat_id)}"
                ),
                meta,
                score,
                matched_line_label=match.label if match else None,
            ))
        return sorted(beat_results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

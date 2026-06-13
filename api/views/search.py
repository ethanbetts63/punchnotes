from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Beat, Bit, Comedian, Episode, Set


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


def first_punchline(beat):
    for line in beat.bit.set.lines.all():
        if (
            line.label == "punchline"
            and beat.line_start <= line.line_number <= beat.line_end
        ):
            return line.text
    return ""


class SearchView(APIView):
    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            empty = {
                "query": "",
                "top_result": None,
                "comedians": [],
                "episodes": [],
                "sets": [],
                "bits": [],
                "jokes": [],
            }
            return Response(empty)

        comedians = self.search_comedians(query)
        episodes = self.search_episodes(query)
        sets = self.search_sets(query)
        bits = self.search_bits(query)
        all_results = comedians + episodes + sets + bits
        top_result = max(all_results, key=lambda item: item["score"], default=None)

        return Response({
            "query": query,
            "top_result": top_result,
            "comedians": comedians,
            "episodes": episodes,
            "sets": sets,
            "bits": bits,
            "jokes": [],
        })

    def search_comedians(self, query):
        rows = (
            Comedian.objects
            .annotate(set_count=Count("sets", distinct=True))
            .filter(
                Q(name__icontains=query)
                | Q(slug__icontains=query)
                | Q(sets__episode__episode_title__icontains=query)
                | Q(sets__bits__summary__icontains=query)
                | Q(sets__bits__beats__premise__icontains=query)
                | Q(sets__lines__text__icontains=query)
            )
            .distinct()
        )
        results = []
        for comedian in rows[:50]:
            meta = [
                fmt_count(comedian.appearance_count, "appearance"),
                fmt_count(comedian.set_count, "set"),
            ]
            if comedian.has_large_joke_book:
                meta.append("large joke book")
            score = text_score(query, comedian.name, comedian.slug) + min(comedian.set_count, 20)
            if score < 25:
                score = 25 + min(comedian.set_count, 20)
            results.append(result(
                "comedian",
                comedian.name,
                "Comedian",
                f"/killtony/comedians/{comedian.slug}",
                meta,
                score,
                image_url=comedian.image_url,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_episodes(self, query):
        number = query.upper().removeprefix("KT").strip().removeprefix("#").strip()
        filters = Q(episode_title__icontains=query)
        if number.isdigit():
            filters |= Q(episode_number=int(number))

        rows = Episode.objects.filter(filters)
        rows = rows | Episode.objects.filter(
            Q(sets__comedian__name__icontains=query)
            | Q(sets__bits__summary__icontains=query)
            | Q(sets__bits__beats__premise__icontains=query)
            | Q(sets__lines__text__icontains=query)
        )
        rows = rows.distinct()
        results = []
        for episode in rows[:50]:
            meta = [
                fmt_count(episode.set_count, "set"),
            ]
            if episode.published_at:
                meta.append(episode.published_at.isoformat())
            if episode.view_count is not None:
                meta.append(f"{episode.view_count:,} views")
            score = text_score(query, episode.episode_title, str(episode.episode_number or ""))
            score += min((episode.view_count or 0) // 100_000, 20)
            if score < 25:
                score = 25 + min(episode.set_count, 20)
            results.append(result(
                "episode",
                episode.episode_title,
                "Episode",
                f"/killtony/episodes/{episode.id}",
                meta,
                score,
                youtube_id=episode.video_id,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_sets(self, query):
        rows = (
            Set.objects
            .select_related("comedian", "episode")
            .filter(
                Q(comedian__name__icontains=query)
                | Q(episode__episode_title__icontains=query)
                | Q(joke_book__icontains=query)
                | Q(bits__summary__icontains=query)
                | Q(bits__beats__premise__icontains=query)
                | Q(lines__text__icontains=query)
            )
            .distinct()
        )
        results = []
        for set_obj in rows[:50]:
            title = f"{set_obj.comedian.name} - KT #{set_obj.episode.episode_number}"
            meta = [
                f"Set {set_obj.set_number}",
                fmt_count(set_obj.bit_count, "bit"),
            ]
            if set_obj.joke_book:
                meta.append(f"{set_obj.joke_book} joke book")
            score = text_score(query, set_obj.comedian.name, set_obj.episode.episode_title, set_obj.joke_book)
            if set_obj.joke_book == "large":
                score += 10
            results.append(result(
                "set",
                title,
                set_obj.episode.episode_title,
                f"/killtony/sets/{set_obj.id}",
                meta,
                score,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_bits(self, query):
        rows = (
            Bit.objects
            .select_related("set__comedian", "set__episode")
            .prefetch_related("beats")
            .filter(Q(summary__icontains=query) | Q(beats__premise__icontains=query))
            .distinct()
        )
        results = []
        for bit in rows[:50]:
            joke_types = set()
            premise_score = 0
            for beat in bit.beats.all():
                if beat.joke_type:
                    joke_types.add(beat.joke_type)
                premise_score = max(premise_score, text_score(query, beat.premise))
            score = text_score(query, bit.summary) + premise_score
            results.append(result(
                "bit",
                bit.summary or f"Bit {bit.bit_id}",
                f"{bit.set.comedian.name} - KT #{bit.set.episode.episode_number}",
                f"/killtony/sets/{bit.set.id}",
                sorted(joke_types)[:3],
                score,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

    def search_jokes(self, query):
        rows = (
            Beat.objects
            .select_related("bit__set__comedian", "bit__set__episode")
            .prefetch_related("bit__set__lines")
            .filter(joke_type__isnull=False)
            .exclude(joke_type="")
            .filter(
                Q(premise__icontains=query)
                | Q(bit__set__lines__text__icontains=query)
                | Q(joke_type__icontains=query)
            )
            .distinct()
        )
        results = []
        for beat in rows[:50]:
            punchline = first_punchline(beat)
            title = punchline or beat.premise or f"{beat.joke_type} joke"
            score = text_score(query, punchline, beat.premise, beat.joke_type)
            results.append(result(
                "joke",
                title,
                f"{beat.bit.set.comedian.name} - KT #{beat.bit.set.episode.episode_number}",
                f"/killtony/sets/{beat.bit.set.id}",
                [beat.joke_type] if beat.joke_type else [],
                score,
            ))
        return sorted(results, key=lambda item: item["score"], reverse=True)[:GROUP_LIMIT]

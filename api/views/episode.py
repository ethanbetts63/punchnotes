from django.db.models import F, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Episode, Set
from api.serializers import EpisodeDetailSerializer, EpisodeListSerializer

SORT_FIELDS = {
    "date":            "published_at",
    "duration":        "duration_seconds",
    "set_count":       "set_count",
    "bucket_pulls":    "bucket_pull_count",
    "golden_tickets":  "golden_ticket_count",
    "large_joke_books": "large_joke_book_count",
    "regulars":        "regular_count",
    "view_count":      "view_count",
    "like_count":      "like_count",
    "like_ratio":      "view_like_ratio",
}


class EpisodeListView(APIView):
    def get(self, request):
        episodes = Episode.objects.prefetch_related("guests")

        q = request.query_params.get("q", "").strip()
        if q:
            number = q.upper().removeprefix("KT").strip().removeprefix("#").strip()
            f = Q(episode_title__icontains=q)
            if number.isdigit():
                f |= Q(episode_number=int(number))
            episodes = episodes.filter(f)

        has = request.query_params.get("has", "").strip()
        if has == "bucket_pull":
            episodes = episodes.filter(bucket_pull_count__gt=0)
        elif has == "golden_ticket":
            episodes = episodes.filter(golden_ticket_count__gt=0)
        elif has == "regular":
            episodes = episodes.filter(regular_count__gt=0)
        elif has == "large_joke_book":
            episodes = episodes.filter(large_joke_book_count__gt=0)

        sort_key = request.query_params.get("sort", "date").strip()
        field = SORT_FIELDS.get(sort_key, "published_at")
        asc = request.query_params.get("asc") == "1"
        order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
        episodes = episodes.order_by(order, "-episode_number")

        return Response(EpisodeListSerializer(episodes, many=True).data)


class EpisodeDetailView(APIView):
    def get(self, request, pk):
        sets_qs = (
            Set.objects
            .select_related("comedian")
            .order_by("start_seconds")
        )
        episode = get_object_or_404(
            Episode.objects.prefetch_related("guests", Prefetch("sets", queryset=sets_qs)),
            pk=pk,
        )
        return Response(EpisodeDetailSerializer(episode).data)

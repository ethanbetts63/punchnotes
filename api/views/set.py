from django.shortcuts import get_object_or_404
from django.db.models import F, Q
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Set
from api.serializers import SetDetailSerializer, SetListSerializer

SORT_FIELDS = {
    "bit_count":           "bit_count",
    "hit_ratio":           "hit_ratio",
    "punchline_tag_ratio": "punchline_tag_ratio",
}


class SetListView(APIView):
    def get(self, request):
        sets = (
            Set.objects
            .select_related("comedian", "episode")
        )

        q = request.query_params.get("q", "").strip()
        if q:
            sets = sets.filter(
                Q(comedian__name__icontains=q) | Q(episode__episode_title__icontains=q)
            )

        attribute = request.query_params.get("attribute", "").strip()
        if attribute:
            sets = sets.filter(comedian__attributes__contains=[attribute])

        joke_book = request.query_params.get("joke_book", "").strip()
        if joke_book in ("small", "medium", "large"):
            sets = sets.filter(joke_book=joke_book)

        sort_key = request.query_params.get("sort", "").strip()
        field = SORT_FIELDS.get(sort_key)
        if field:
            asc = request.query_params.get("asc") == "1"
            order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
            sets = sets.order_by(order)
        else:
            sets = sets.order_by("-episode__episode_number", "start_seconds")

        return Response(SetListSerializer(sets, many=True).data)


class SetDetailView(APIView):
    def get(self, request, pk):
        set_obj = get_object_or_404(
            Set.objects
            .select_related("comedian", "episode")
            .prefetch_related("lines", "bits__beats"),
            pk=pk,
        )
        return Response(SetDetailSerializer(set_obj).data)

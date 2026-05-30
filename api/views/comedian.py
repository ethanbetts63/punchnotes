from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Comedian, Set
from api.serializers import ComedianDetailSerializer, ComedianListSerializer


class ComedianListView(APIView):
    def get(self, request):
        comedians = (
            Comedian.objects
            .annotate(
                set_count=Count("sets", distinct=True),
                appearances=Count("sets__episode", distinct=True),
            )
            .order_by("name")
        )

        q = request.query_params.get("q", "").strip()
        if q:
            comedians = comedians.filter(name__icontains=q)

        attribute = request.query_params.get("attribute", "").strip()
        if attribute:
            comedians = comedians.filter(attributes__contains=[attribute])

        joke_book = request.query_params.get("joke_book", "").strip()
        if joke_book == "small":
            comedians = comedians.filter(has_small_joke_book=True)
        elif joke_book == "medium":
            comedians = comedians.filter(has_medium_joke_book=True)
        elif joke_book == "large":
            comedians = comedians.filter(has_large_joke_book=True)

        return Response(ComedianListSerializer(comedians, many=True).data)


class ComedianDetailView(APIView):
    def get(self, request, slug):
        comedian = get_object_or_404(
            Comedian.objects.prefetch_related(
                Prefetch(
                    "sets",
                    queryset=Set.objects.select_related("episode").order_by("-episode__episode_number"),
                )
            ),
            slug=slug,
        )
        return Response(ComedianDetailSerializer(comedian).data)

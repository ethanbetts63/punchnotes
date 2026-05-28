from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Episode, Set
from api.serializers import EpisodeDetailSerializer, EpisodeListSerializer


class EpisodeListView(APIView):
    def get(self, request):
        episodes = (
            Episode.objects
            .annotate(set_count=Count("sets"))
            .order_by("-episode_number")
        )
        return Response(EpisodeListSerializer(episodes, many=True).data)


class EpisodeDetailView(APIView):
    def get(self, request, pk):
        sets_qs = (
            Set.objects
            .annotate(bit_count=Count("bits"))
            .select_related("comedian")
            .order_by("start_seconds")
        )
        episode = get_object_or_404(
            Episode.objects.prefetch_related(Prefetch("sets", queryset=sets_qs)),
            pk=pk,
        )
        return Response(EpisodeDetailSerializer(episode).data)

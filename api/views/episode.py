from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Episode, Set
from api.serializers import EpisodeDetailSerializer, EpisodeListSerializer
from .querysets import build_episode_list_queryset


class EpisodeListView(APIView):
    def get(self, request):
        episodes = build_episode_list_queryset(request.query_params)
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

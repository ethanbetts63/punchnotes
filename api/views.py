from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Beat, Comedian, Episode, Set
from .serializers import (
    ComedianDetailSerializer,
    ComedianListSerializer,
    EpisodeDetailSerializer,
    EpisodeListSerializer,
    JokeSerializer,
    SetDetailSerializer,
)


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
        )
        episode = get_object_or_404(
            Episode.objects.prefetch_related(Prefetch("sets", queryset=sets_qs)),
            pk=pk,
        )
        return Response(EpisodeDetailSerializer(episode).data)


class ComedianListView(APIView):
    def get(self, request):
        comedians = (
            Comedian.objects
            .annotate(set_count=Count("sets"), appearances=Count("guest_appearances"))
            .order_by("name")
        )
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


class SetDetailView(APIView):
    def get(self, request, pk):
        set_obj = get_object_or_404(
            Set.objects
            .select_related("comedian", "episode")
            .prefetch_related("lines", "bits__beats"),
            pk=pk,
        )
        return Response(SetDetailSerializer(set_obj).data)


class JokeListView(APIView):
    def get(self, request):
        beats = (
            Beat.objects
            .select_related("bit__set__comedian", "bit__set__episode")
            .prefetch_related("bit__set__lines")
            .filter(joke_type__isnull=False)
            .exclude(joke_type="")
        )
        joke_type = request.query_params.get("joke_type")
        if joke_type:
            beats = beats.filter(joke_type=joke_type)
        topic = request.query_params.get("topic")
        if topic:
            beats = beats.filter(topics__contains=topic)
        return Response(JokeSerializer(beats, many=True).data)

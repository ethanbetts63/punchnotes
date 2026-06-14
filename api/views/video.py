from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Video, Set
from api.serializers import VideoDetailSerializer, VideoListSerializer
from .querysets import build_video_list_queryset


class VideoListView(APIView):
    def get(self, request):
        videos = build_video_list_queryset(request.query_params)
        return Response(VideoListSerializer(videos, many=True).data)


class VideoDetailView(APIView):
    def get(self, request, pk):
        sets_qs = (
            Set.objects
            .select_related("comedian")
            .order_by("start_seconds")
        )
        video = get_object_or_404(
            Video.objects.prefetch_related("guests", Prefetch("sets", queryset=sets_qs)),
            pk=pk,
        )
        return Response(VideoDetailSerializer(video).data)

from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView

from pipeline.models import Video, Set
from api.serializers import VideoDetailSerializer, VideoListSerializer
from .querysets import build_video_list_queryset


class VideoListView(ListAPIView):
    serializer_class = VideoListSerializer

    def get_queryset(self):
        return build_video_list_queryset(self.request.query_params)


class VideoDetailView(RetrieveAPIView):
    serializer_class = VideoDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        sets_qs = (
            Set.objects
            .select_related("comedian")
            .order_by("start_seconds")
        )
        return Video.objects.prefetch_related(
            "guests",
            Prefetch("sets", queryset=sets_qs),
        )

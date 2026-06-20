from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView

from pipeline.models import Video, Set
from api.serializers import VideoDetailSerializer, VideoListSerializer
from api.video_slugs import lookup_video_by_public_slug
from .querysets import build_video_list_queryset


class VideoListView(ListAPIView):
    serializer_class = VideoListSerializer

    def get_queryset(self):
        return build_video_list_queryset(self.request.query_params)


class VideoDetailView(RetrieveAPIView):
    serializer_class = VideoDetailSerializer
    lookup_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def get_queryset(self):
        sets_qs = (
            Set.objects
            .select_related("comedian")
            .order_by("start_seconds")
        )
        qs = Video.objects.prefetch_related(Prefetch("sets", queryset=sets_qs))
        slug = self.kwargs.get(self.lookup_url_kwarg or "slug", "")
        if str(slug).isdigit():
            return qs.filter(pk=int(slug))
        return lookup_video_by_public_slug(slug).prefetch_related(Prefetch("sets", queryset=sets_qs))

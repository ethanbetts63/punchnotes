from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.shortcuts import get_object_or_404

from api.serializers import SetDetailSerializer, SetListSerializer
from api.set_slugs import lookup_set_by_public_slug
from .querysets import build_set_list_queryset


class SetListView(ListAPIView):
    serializer_class = SetListSerializer

    def get_queryset(self):
        return build_set_list_queryset(self.request.query_params)


class SetDetailView(RetrieveAPIView):
    serializer_class = SetDetailSerializer
    lookup_url_kwarg = "slug"

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def get_queryset(self):
        slug = self.kwargs.get(self.lookup_url_kwarg or "slug", "")
        return lookup_set_by_public_slug(slug).select_related(
            "comedian",
            "video",
        ).prefetch_related(
            "lines",
            "bits__beats",
        )

from rest_framework.generics import ListAPIView, RetrieveAPIView

from pipeline.models import Set
from api.serializers import SetDetailSerializer, SetListSerializer
from .querysets import build_set_list_queryset


class SetListView(ListAPIView):
    serializer_class = SetListSerializer

    def get_queryset(self):
        return build_set_list_queryset(self.request.query_params)


class SetDetailView(RetrieveAPIView):
    serializer_class = SetDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Set.objects.select_related(
            "comedian",
            "video",
        ).prefetch_related(
            "lines",
            "bits__beats",
        )

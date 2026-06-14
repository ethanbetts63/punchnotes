from rest_framework.generics import ListAPIView, RetrieveAPIView

from api.serializers import ComedianDetailSerializer, ComedianListSerializer
from .querysets import build_comedian_detail_queryset, build_comedian_list_queryset


class ComedianListView(ListAPIView):
    serializer_class = ComedianListSerializer

    def get_queryset(self):
        return build_comedian_list_queryset(self.request.query_params)


class ComedianDetailView(RetrieveAPIView):
    serializer_class = ComedianDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return build_comedian_detail_queryset()

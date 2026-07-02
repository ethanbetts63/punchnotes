from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from api.serializers import ComedianDetailSerializer, ComedianListSerializer
from .querysets import build_comedian_detail_queryset, build_comedian_list_queryset


class ComedianListView(ListAPIView):
    serializer_class = ComedianListSerializer
    permission_classes = [AllowAny]
    throttle_scope = "catalogue"

    def get_queryset(self):
        return build_comedian_list_queryset(self.request.query_params)


class ComedianDetailView(RetrieveAPIView):
    serializer_class = ComedianDetailSerializer
    permission_classes = [AllowAny]
    throttle_scope = "catalogue"
    lookup_field = "slug"

    def get_queryset(self):
        return build_comedian_detail_queryset()

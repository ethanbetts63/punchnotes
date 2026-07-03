from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from api.serializers import BeatSearchSerializer
from .querysets import build_beat_search_queryset


class BeatPagination(PageNumberPagination):
    page_size = 20


class BeatListView(ListAPIView):
    serializer_class = BeatSearchSerializer
    permission_classes = [AllowAny]
    throttle_scope = "search"
    pagination_class = BeatPagination

    def get_queryset(self):
        return build_beat_search_queryset(self.request.query_params)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        query = (self.request.query_params.get("q") or "").strip()
        context["query"] = query
        return context

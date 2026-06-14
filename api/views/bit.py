from rest_framework.generics import ListAPIView

from api.serializers import BitListSerializer
from .querysets import build_bit_list_queryset


class BitListView(ListAPIView):
    serializer_class = BitListSerializer

    def get_queryset(self):
        return build_bit_list_queryset(self.request.query_params)

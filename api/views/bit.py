from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import BitListSerializer
from .querysets import build_bit_list_queryset


class BitListView(APIView):
    def get(self, request):
        bits = build_bit_list_queryset(request.query_params)
        return Response(BitListSerializer(list(bits), many=True).data)

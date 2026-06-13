from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ComedianDetailSerializer, ComedianListSerializer
from .querysets import build_comedian_detail_queryset, build_comedian_list_queryset


class ComedianListView(APIView):
    def get(self, request):
        comedians = build_comedian_list_queryset(request.query_params)
        return Response(ComedianListSerializer(comedians, many=True).data)


class ComedianDetailView(APIView):
    def get(self, request, slug):
        comedian = get_object_or_404(
            build_comedian_detail_queryset(),
            slug=slug,
        )
        return Response(ComedianDetailSerializer(comedian).data)

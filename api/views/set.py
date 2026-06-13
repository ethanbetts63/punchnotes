from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Set
from api.serializers import SetDetailSerializer, SetListSerializer
from .querysets import build_set_list_queryset


class SetListView(APIView):
    def get(self, request):
        sets = build_set_list_queryset(request.query_params)
        return Response(SetListSerializer(sets, many=True).data)


class SetDetailView(APIView):
    def get(self, request, pk):
        set_obj = get_object_or_404(
            Set.objects
            .select_related("comedian", "episode")
            .prefetch_related("lines", "bits__beats"),
            pk=pk,
        )
        return Response(SetDetailSerializer(set_obj).data)

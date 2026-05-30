from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Set
from api.serializers import SetDetailSerializer, SetListSerializer


class SetListView(APIView):
    def get(self, request):
        sets = (
            Set.objects
            .select_related("comedian", "episode")
            .annotate(bit_count=Count("bits", distinct=True))
            .order_by("-episode__episode_number", "start_seconds")
        )
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

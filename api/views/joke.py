from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import BeatSearchSerializer
from .querysets import build_beat_search_queryset


class BeatListView(APIView):
    def get(self, request):
        beats = build_beat_search_queryset(request.query_params)
        query = (request.query_params.get("q") or "").strip()
        context = {"query": query}
        return Response(BeatSearchSerializer(list(beats), many=True, context=context).data)

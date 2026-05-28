from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Beat


class TopicListView(APIView):
    def get(self, request):
        topics: set[str] = set()
        for row in Beat.objects.exclude(topics=[]).values_list("topics", flat=True):
            topics.update(row)
        return Response(sorted(topics, key=str.lower))

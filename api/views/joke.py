from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Beat
from api.serializers import JokeSerializer


class JokeListView(APIView):
    def get(self, request):
        beats = (
            Beat.objects
            .select_related("bit__set__comedian", "bit__set__episode")
            .prefetch_related("bit__set__lines")
            .filter(joke_type__isnull=False)
            .exclude(joke_type="")
        )
        joke_type = request.query_params.get("joke_type")
        if joke_type:
            beats = beats.filter(joke_type=joke_type)
        topic = request.query_params.get("topic")
        if topic:
            beats = beats.filter(topics__contains=topic)
        return Response(JokeSerializer(beats, many=True).data)

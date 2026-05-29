from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

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
        query = request.query_params.get("q", "").strip()
        if query:
            beats = beats.filter(
                Q(premise__icontains=query)
                | Q(joke_type__icontains=query)
                | Q(bit__summary__icontains=query)
                | Q(bit__set__comedian__name__icontains=query)
                | Q(bit__set__episode__episode_title__icontains=query)
                | Q(bit__set__lines__text__icontains=query)
            ).distinct()
        topic = request.query_params.get("topic")
        evaluated = list(beats)
        if topic:
            evaluated = [b for b in evaluated if topic in (b.topics or [])]
        return Response(JokeSerializer(evaluated, many=True).data)

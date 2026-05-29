from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from pipeline.models import Bit
from api.serializers import BitListSerializer


class BitListView(APIView):
    def get(self, request):
        bits = (
            Bit.objects
            .select_related("set__comedian", "set__episode")
            .prefetch_related("beats")
            .filter(beats__isnull=False)
            .distinct()
        )

        joke_type = request.query_params.get("joke_type")
        if joke_type:
            bits = bits.filter(beats__joke_type=joke_type)

        query = request.query_params.get("q", "").strip()
        if query:
            bits = bits.filter(
                Q(summary__icontains=query)
                | Q(beats__premise__icontains=query)
                | Q(beats__joke_type__icontains=query)
                | Q(set__comedian__name__icontains=query)
                | Q(set__episode__episode_title__icontains=query)
            ).distinct()

        evaluated = list(bits)

        topic = request.query_params.get("topic")
        if topic:
            evaluated = [
                b for b in evaluated
                if any(topic in (beat.topics or []) for beat in b.beats.all())
            ]

        return Response(BitListSerializer(evaluated, many=True).data)

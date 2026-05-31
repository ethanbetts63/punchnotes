from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F, Q

from pipeline.models import Bit
from api.serializers import BitListSerializer

SORT_FIELDS = {
    "hit_ratio":           "hit_ratio",
    "punchline_tag_ratio": "punchline_tag_ratio",
}


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

        topic = request.query_params.get("topic")
        if topic:
            bits = bits.filter(beats__topics__contains=[topic]).distinct()

        sort_key = request.query_params.get("sort", "").strip()
        field = SORT_FIELDS.get(sort_key)
        if field:
            asc = request.query_params.get("asc") == "1"
            order = F(field).asc(nulls_last=True) if asc else F(field).desc(nulls_last=True)
            bits = bits.order_by(order)

        return Response(BitListSerializer(list(bits), many=True).data)

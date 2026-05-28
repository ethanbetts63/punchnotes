from rest_framework import serializers

from pipeline.models import Beat, Bit, Line, Set
from .shared import ComedianMinimalSerializer, EpisodeMinimalSerializer


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["id", "line_number", "label", "text", "start_seconds"]


class BeatSerializer(serializers.ModelSerializer):
    lines = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = ["id", "beat_id", "premise", "joke_type", "topics", "line_start", "line_end", "lines"]

    def get_lines(self, beat):
        set_lines = self.context.get("set_lines", [])
        lines = [l for l in set_lines if beat.line_start <= l.line_number <= beat.line_end]
        return LineSerializer(lines, many=True).data


class BitSerializer(serializers.ModelSerializer):
    beats = BeatSerializer(many=True)

    class Meta:
        model = Bit
        fields = ["id", "bit_id", "premise", "line_start", "line_end", "beats"]


class SetDetailSerializer(serializers.ModelSerializer):
    comedian = ComedianMinimalSerializer()
    episode = EpisodeMinimalSerializer()
    joke_book_award = serializers.CharField(source="joke_book", allow_null=True)
    bits = serializers.SerializerMethodField()

    class Meta:
        model = Set
        fields = ["id", "set_number", "comedian", "episode", "joke_book_award", "start_seconds", "bits"]

    def get_bits(self, set_obj):
        lines = list(set_obj.lines.all())
        context = {**self.context, "set_lines": lines}
        return BitSerializer(set_obj.bits.prefetch_related("beats"), many=True, context=context).data

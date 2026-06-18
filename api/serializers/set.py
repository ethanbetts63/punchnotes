from rest_framework import serializers

from pipeline.models import Beat, Bit, Comedian, Line, Set
from .fields import AbsoluteMediaUrlField
from .shared import VideoMinimalSerializer


class ComedianForSetSerializer(serializers.ModelSerializer):
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count",
            "avg_bits_per_set", "avg_beats_per_set",
            "avg_punch_density", "avg_tag_density",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
        ]



class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["id", "line_number", "label", "text", "start_seconds"]


class BeatSerializer(serializers.ModelSerializer):
    lines = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = ["id", "beat_id", "premise", "joke_type", "line_start", "line_end", "lines"]

    def get_lines(self, beat):
        set_lines = self.context.get("set_lines", [])
        lines = [l for l in set_lines if beat.line_start <= l.line_number <= beat.line_end]
        return LineSerializer(lines, many=True).data


class BitSerializer(serializers.ModelSerializer):
    beats = BeatSerializer(many=True)

    class Meta:
        model = Bit
        fields = ["id", "bit_id", "summary", "line_start", "line_end", "beats"]


class SetDetailSerializer(serializers.ModelSerializer):
    comedian = ComedianForSetSerializer()
    video = VideoMinimalSerializer()
    bits = serializers.SerializerMethodField()
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "video",
            "attributes", "start_seconds",
            "image_url", "image_capture_seconds",
            "punch_density", "tag_density",
            "bits",
        ]

    def get_bits(self, set_obj):
        lines = list(set_obj.lines.all())
        context = {**self.context, "set_lines": lines}
        return BitSerializer(set_obj.bits.all(), many=True, context=context).data


class SetListSerializer(serializers.ModelSerializer):
    comedian = ComedianForSetSerializer()
    video = VideoMinimalSerializer()
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "video",
            "attributes", "start_seconds", "interview_end_seconds",
            "image_url", "image_capture_seconds",
            "punch_density", "tag_density", "bit_count",
        ]

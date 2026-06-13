from rest_framework import serializers

from pipeline.models import Beat, Bit, Comedian, Line, Set
from .shared import EpisodeMinimalSerializer


class ComedianForSetSerializer(serializers.ModelSerializer):
    set_count = serializers.SerializerMethodField()
    appearances = serializers.SerializerMethodField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count", "appearances",
            "avg_bits_per_set", "avg_beats_per_set",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
        ]

    def get_set_count(self, obj):
        return obj.sets.count()

    def get_appearances(self, obj):
        return obj.appearance_count


class ComedianForSetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "avg_bits_per_set", "avg_beats_per_set",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
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
    episode = EpisodeMinimalSerializer()
    bits = serializers.SerializerMethodField()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "episode",
            "attributes", "start_seconds",
            "image_url", "image_capture_seconds",
            "hit_ratio", "punchline_tag_ratio",
            "bits",
        ]

    def get_bits(self, set_obj):
        lines = list(set_obj.lines.all())
        context = {**self.context, "set_lines": lines}
        return BitSerializer(set_obj.bits.prefetch_related("beats"), many=True, context=context).data


class SetListSerializer(serializers.ModelSerializer):
    comedian = ComedianForSetListSerializer()
    episode = EpisodeMinimalSerializer()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "episode",
            "attributes", "start_seconds", "interview_end_seconds",
            "image_url", "image_capture_seconds",
            "hit_ratio", "punchline_tag_ratio", "bit_count",
        ]

from rest_framework import serializers

from pipeline.models import Comedian, Set
from .shared import EpisodeMinimalSerializer


class SetInComedianSerializer(serializers.ModelSerializer):
    episode = EpisodeMinimalSerializer()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "episode", "joke_book",
            "hit_ratio", "punchline_tag_ratio",
            "image_url", "image_capture_seconds",
        ]


class ComedianListSerializer(serializers.ModelSerializer):
    set_count = serializers.IntegerField()
    appearances = serializers.IntegerField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count", "appearances",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
            "avg_bits_per_set", "avg_beats_per_set",
        ]


class ComedianDetailSerializer(serializers.ModelSerializer):
    sets = SetInComedianSerializer(many=True)
    set_count = serializers.SerializerMethodField()
    appearances = serializers.SerializerMethodField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count", "appearances",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
            "avg_bits_per_set", "avg_beats_per_set",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
            "sets",
        ]

    def get_set_count(self, obj):
        return obj.sets.count()

    def get_appearances(self, obj):
        return obj.sets.values("episode").distinct().count()

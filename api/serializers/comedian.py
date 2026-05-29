from rest_framework import serializers

from pipeline.models import Comedian, Set
from .shared import EpisodeMinimalSerializer


class SetInComedianSerializer(serializers.ModelSerializer):
    episode = EpisodeMinimalSerializer()

    class Meta:
        model = Set
        fields = ["id", "set_number", "episode", "joke_book", "hit_ratio", "punchline_tag_ratio"]


class ComedianListSerializer(serializers.ModelSerializer):
    set_count = serializers.IntegerField()
    appearances = serializers.IntegerField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "comedian_type", "attributes",
            "set_count", "appearances",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
            "avg_bits_per_set", "avg_beats_per_set",
        ]


class ComedianDetailSerializer(serializers.ModelSerializer):
    sets = SetInComedianSerializer(many=True)

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "comedian_type", "attributes",
            "avg_hit_ratio", "avg_punchline_tag_ratio",
            "avg_bits_per_set", "avg_beats_per_set",
            "sets",
        ]

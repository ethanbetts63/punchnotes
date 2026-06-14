from rest_framework import serializers

from pipeline.models import Comedian, Set
from .shared import VideoMinimalSerializer


class SetInComedianSerializer(serializers.ModelSerializer):
    video = VideoMinimalSerializer()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "video", "attributes",
            "punch_density", "tag_density",
            "image_url", "image_capture_seconds",
        ]


class ComedianListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
            "avg_punch_density", "avg_tag_density",
            "avg_bits_per_set", "avg_beats_per_set",
        ]


class ComedianDetailSerializer(ComedianListSerializer):
    sets = SetInComedianSerializer(many=True)

    class Meta(ComedianListSerializer.Meta):
        fields = ComedianListSerializer.Meta.fields + ["sets"]

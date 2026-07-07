from rest_framework import serializers

from pipeline.models import Comedian, Set
from .fields import AbsoluteMediaUrlField
from .shared import PublicSetSlugMixin, VideoMinimalSerializer


class SetInComedianSerializer(PublicSetSlugMixin, serializers.ModelSerializer):
    video = VideoMinimalSerializer()
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Set
        fields = [
            "id", "slug", "video", "attributes",
            "start_seconds", "bit_count",
            "punch_density", "tag_density",
            "image_url", "image_capture_seconds",
        ]


class ComedianListSerializer(serializers.ModelSerializer):
    image_url = AbsoluteMediaUrlField()

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

from rest_framework import serializers

from pipeline.models import Bit
from api.set_slugs import set_public_slug


class BitListSerializer(serializers.ModelSerializer):
    comedian = serializers.CharField(source="set.comedian.name")
    comedian_slug = serializers.CharField(source="set.comedian.slug")
    episode_number = serializers.IntegerField(source="set.video.number")
    set_slug = serializers.SerializerMethodField()
    joke_types = serializers.SerializerMethodField()
    beats = serializers.SerializerMethodField()

    class Meta:
        model = Bit
        fields = [
            "id", "bit_id", "comedian", "comedian_slug", "episode_number", "set_slug",
            "joke_types", "beats",
            "punch_density", "tag_density",
        ]

    def get_set_slug(self, bit):
        return set_public_slug(bit.set)

    def get_joke_types(self, bit):
        return sorted({
            beat.joke_type
            for beat in bit.beats.all()
            if beat.joke_type
        })

    def get_beats(self, bit):
        return [
            {"beat_id": beat.beat_id, "premise": beat.premise, "joke_type": beat.joke_type or ""}
            for beat in bit.beats.all()
            if beat.premise
        ]

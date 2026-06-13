from rest_framework import serializers

from pipeline.models import Bit


class BitListSerializer(serializers.ModelSerializer):
    comedian = serializers.CharField(source="set.comedian.name")
    comedian_slug = serializers.CharField(source="set.comedian.slug")
    episode_number = serializers.IntegerField(source="set.episode.episode_number")
    set_id = serializers.IntegerField(source="set.id")
    joke_types = serializers.SerializerMethodField()
    beats_summary = serializers.SerializerMethodField()

    class Meta:
        model = Bit
        fields = [
            "id", "comedian", "comedian_slug", "episode_number", "set_id",
            "summary", "joke_types", "beats_summary",
            "hit_ratio", "punchline_tag_ratio",
        ]

    def get_joke_types(self, bit):
        return list(
            bit.beats
            .filter(joke_type__isnull=False)
            .exclude(joke_type="")
            .values_list("joke_type", flat=True)
            .distinct()
        )

    def get_beats_summary(self, bit):
        return [
            {"premise": beat.premise, "joke_type": beat.joke_type or ""}
            for beat in bit.beats.all()
            if beat.premise
        ]

from rest_framework import serializers

from pipeline.models import Beat
from api.beat_utils import describe_beat_lines
from api.set_slugs import set_public_slug


class BeatSearchSerializer(serializers.ModelSerializer):
    comedian = serializers.CharField(source="bit.set.comedian.name")
    comedian_slug = serializers.CharField(source="bit.set.comedian.slug")
    episode_number = serializers.IntegerField(source="bit.set.video.number")
    set_slug = serializers.SerializerMethodField()
    bit_id = serializers.CharField(source="bit.bit_id")
    setup_lines = serializers.SerializerMethodField()
    punchline = serializers.SerializerMethodField()
    matched_line = serializers.SerializerMethodField()
    matched_line_label = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = [
            "id", "beat_id", "bit_id", "comedian", "comedian_slug", "episode_number", "set_slug",
            "joke_type", "setup_lines", "punchline",
            "matched_line", "matched_line_label",
        ]

    def get_set_slug(self, beat):
        return set_public_slug(beat.bit.set)

    def _beat_data(self, beat):
        cache = self.context.setdefault("beat_line_data", {})
        if beat.id not in cache:
            cache[beat.id] = describe_beat_lines(
                beat,
                query=self.context.get("query", ""),
            )
        return cache[beat.id]

    def get_setup_lines(self, beat):
        return self._beat_data(beat)["setup_lines"]

    def get_punchline(self, beat):
        return self._beat_data(beat)["punchline"]

    def get_matched_line(self, beat):
        line = self._beat_data(beat)["matched_line"]
        return line.text if line else ""

    def get_matched_line_label(self, beat):
        line = self._beat_data(beat)["matched_line"]
        return line.label if line else ""

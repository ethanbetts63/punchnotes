from rest_framework import serializers

from pipeline.models import Beat


class JokeSerializer(serializers.ModelSerializer):
    comedian = serializers.CharField(source="bit.set.comedian.name")
    comedian_slug = serializers.CharField(source="bit.set.comedian.slug")
    episode_number = serializers.IntegerField(source="bit.set.episode.episode_number")
    set_id = serializers.IntegerField(source="bit.set.id")
    setup_lines = serializers.SerializerMethodField()
    punchline = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = [
            "id", "comedian", "comedian_slug", "episode_number", "set_id",
            "premise", "joke_type", "keys", "setup_lines", "punchline",
        ]

    def get_setup_lines(self, beat):
        return list(
            beat.bit.set.lines
            .filter(label="setup", line_number__range=(beat.line_start, beat.line_end))
            .values_list("text", flat=True)
        )

    def get_punchline(self, beat):
        line = beat.bit.set.lines.filter(
            label="punchline", line_number__range=(beat.line_start, beat.line_end)
        ).first()
        return line.text if line else ""

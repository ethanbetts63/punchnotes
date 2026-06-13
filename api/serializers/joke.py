from rest_framework import serializers

from pipeline.models import Beat


SEARCHABLE_BEAT_LINE_LABELS = {"setup", "punchline", "tag"}


def beat_lines(beat):
    return [
        line
        for line in beat.bit.set.lines.all()
        if beat.line_start <= line.line_number <= beat.line_end
    ]


def setup_lines_for_beat(beat):
    return [line.text for line in beat_lines(beat) if line.label == "setup"]


def punchline_text_for_beat(beat):
    for line in beat_lines(beat):
        if line.label == "punchline":
            return line.text
    return ""


def matching_line_for_beat(beat, query):
    if not query:
        return None

    query_lower = query.lower()
    for line in beat_lines(beat):
        if line.label in SEARCHABLE_BEAT_LINE_LABELS and query_lower in line.text.lower():
            return line
    return None


class BeatSearchSerializer(serializers.ModelSerializer):
    comedian = serializers.CharField(source="bit.set.comedian.name")
    comedian_slug = serializers.CharField(source="bit.set.comedian.slug")
    episode_number = serializers.IntegerField(source="bit.set.episode.episode_number")
    set_id = serializers.IntegerField(source="bit.set.id")
    setup_lines = serializers.SerializerMethodField()
    punchline = serializers.SerializerMethodField()
    matched_line = serializers.SerializerMethodField()
    matched_line_label = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = [
            "id", "comedian", "comedian_slug", "episode_number", "set_id",
            "premise", "joke_type", "setup_lines", "punchline",
            "matched_line", "matched_line_label",
        ]

    def get_setup_lines(self, beat):
        return setup_lines_for_beat(beat)

    def get_punchline(self, beat):
        return punchline_text_for_beat(beat)

    def get_matched_line(self, beat):
        line = matching_line_for_beat(beat, self.context.get("query", ""))
        return line.text if line else ""

    def get_matched_line_label(self, beat):
        line = matching_line_for_beat(beat, self.context.get("query", ""))
        return line.label if line else ""

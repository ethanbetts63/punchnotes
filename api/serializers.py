from rest_framework import serializers

from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


class ComedianMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = ["id", "name", "slug"]


class EpisodeMinimalSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    date = serializers.DateField(source="published_at")

    class Meta:
        model = Episode
        fields = ["id", "number", "title", "date"]


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["id", "line_number", "label", "text", "start_seconds"]


class BeatSerializer(serializers.ModelSerializer):
    lines = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = ["id", "beat_id", "premise", "joke_type", "topics", "line_start", "line_end", "lines"]

    def get_lines(self, beat):
        set_lines = self.context.get("set_lines", [])
        lines = [l for l in set_lines if beat.line_start <= l.line_number <= beat.line_end]
        return LineSerializer(lines, many=True).data


class BitSerializer(serializers.ModelSerializer):
    beats = BeatSerializer(many=True)

    class Meta:
        model = Bit
        fields = ["id", "bit_id", "premise", "line_start", "line_end", "beats"]


class SetDetailSerializer(serializers.ModelSerializer):
    comedian = ComedianMinimalSerializer()
    episode = EpisodeMinimalSerializer()
    joke_book_award = serializers.CharField(source="joke_book", allow_null=True)
    bits = serializers.SerializerMethodField()

    class Meta:
        model = Set
        fields = ["id", "set_number", "comedian", "episode", "joke_book_award", "bits"]

    def get_bits(self, set_obj):
        lines = list(set_obj.lines.all())
        context = {**self.context, "set_lines": lines}
        return BitSerializer(set_obj.bits.prefetch_related("beats"), many=True, context=context).data


class SetInEpisodeSerializer(serializers.ModelSerializer):
    comedian = ComedianMinimalSerializer()
    bit_count = serializers.IntegerField()

    class Meta:
        model = Set
        fields = ["id", "set_number", "comedian", "joke_book", "bit_count", "start_seconds", "interview_end_seconds"]


class EpisodeListSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    date = serializers.DateField(source="published_at")
    set_count = serializers.IntegerField()

    class Meta:
        model = Episode
        fields = ["id", "number", "title", "date", "set_count"]


class EpisodeDetailSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    url = serializers.URLField(source="episode_url")
    date = serializers.DateField(source="published_at")
    sets = SetInEpisodeSerializer(many=True)

    class Meta:
        model = Episode
        fields = ["id", "number", "title", "url", "date", "sets"]


class ComedianListSerializer(serializers.ModelSerializer):
    set_count = serializers.IntegerField()
    appearances = serializers.IntegerField()

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "comedian_type", "set_count", "appearances"]


class SetInComedianSerializer(serializers.ModelSerializer):
    episode = EpisodeMinimalSerializer()

    class Meta:
        model = Set
        fields = ["id", "set_number", "episode", "joke_book"]


class ComedianDetailSerializer(serializers.ModelSerializer):
    sets = SetInComedianSerializer(many=True)

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "comedian_type", "sets"]


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
            "premise", "joke_type", "topics", "setup_lines", "punchline",
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

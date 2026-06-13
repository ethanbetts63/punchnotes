from rest_framework import serializers

from pipeline.models import Episode, Set
from .shared import ComedianMinimalSerializer


class SetInEpisodeSerializer(serializers.ModelSerializer):
    comedian = ComedianMinimalSerializer()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "attributes", "bit_count",
            "start_seconds", "interview_end_seconds",
            "image_url", "image_capture_seconds",
        ]


class EpisodeListSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    date = serializers.DateField(source="published_at")
    youtube_id = serializers.CharField(source="video_id")
    guests = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Episode
        fields = [
            "id", "number", "title", "date", "youtube_id", "guests", "set_count",
            "duration_seconds",
            "bucket_pull_count", "golden_ticket_count",
            "regular_count", "large_joke_book_count",
            "view_count", "like_count", "comment_count", "view_like_ratio",
        ]


class EpisodeDetailSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    url = serializers.URLField(source="episode_url")
    youtube_id = serializers.CharField(source="video_id")
    date = serializers.DateField(source="published_at")
    guests = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    sets = serializers.SerializerMethodField()

    class Meta:
        model = Episode
        fields = [
            "id", "number", "title", "url", "youtube_id", "date", "guests",
            "duration_seconds",
            "bucket_pull_count", "golden_ticket_count",
            "regular_count", "large_joke_book_count",
            "view_count", "like_count", "comment_count",
            "sets",
        ]

    def get_sets(self, episode):
        ordered = sorted(episode.sets.all(), key=lambda s: s.start_seconds)
        return SetInEpisodeSerializer(ordered, many=True).data

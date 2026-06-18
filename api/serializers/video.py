from rest_framework import serializers

from pipeline.models import Video, Set
from .shared import ComedianMinimalSerializer


class SetInVideoSerializer(serializers.ModelSerializer):
    comedian = ComedianMinimalSerializer()

    class Meta:
        model = Set
        fields = [
            "id", "set_number", "comedian", "attributes", "bit_count",
            "start_seconds", "interview_end_seconds",
            "image_url", "image_capture_seconds",
        ]


class VideoListSerializer(serializers.ModelSerializer):
    youtube_id = serializers.CharField(source="video_id")

    class Meta:
        model = Video
        fields = [
            "id", "number", "title", "url", "date", "youtube_id", "guests", "set_count",
            "duration_seconds",
            "bucket_pull_count", "golden_ticket_count",
            "regular_count", "large_joke_book_count",
            "view_count", "like_count", "comment_count", "view_like_ratio",
        ]


class VideoDetailSerializer(VideoListSerializer):
    sets = serializers.SerializerMethodField()

    class Meta(VideoListSerializer.Meta):
        fields = VideoListSerializer.Meta.fields + ["sets"]

    def get_sets(self, video):
        return SetInVideoSerializer(video.sets.all(), many=True).data

from rest_framework import serializers

from pipeline.models import Video, Set
from api.set_slugs import set_public_slug
from api.video_slugs import video_public_slug
from .fields import AbsoluteMediaUrlField
from .shared import ComedianMinimalSerializer


class SetInVideoSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    comedian = ComedianMinimalSerializer()
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Set
        fields = [
            "id", "slug", "set_number", "comedian", "attributes", "bit_count",
            "start_seconds", "interview_end_seconds",
            "image_url", "image_capture_seconds",
            "punch_density", "tag_density",
        ]

    def get_slug(self, set_obj):
        return set_public_slug(set_obj)


class VideoListSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    youtube_id = serializers.CharField(source="video_id")

    class Meta:
        model = Video
        fields = [
            "id", "slug", "number", "title", "url", "date", "youtube_id", "guests", "set_count",
            "duration_seconds",
            "bucket_pull_count", "golden_ticket_count",
            "regular_count", "large_joke_book_count",
            "view_count", "like_count", "comment_count", "view_like_ratio",
        ]

    def get_slug(self, video):
        return video_public_slug(video)


class VideoDetailSerializer(VideoListSerializer):
    sets = serializers.SerializerMethodField()

    class Meta(VideoListSerializer.Meta):
        fields = VideoListSerializer.Meta.fields + ["sets"]

    def get_sets(self, video):
        return SetInVideoSerializer(video.sets.all(), many=True, context=self.context).data

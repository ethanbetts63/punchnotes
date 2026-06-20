from rest_framework import serializers

from pipeline.models import Comedian, Video
from api.video_slugs import video_public_slug
from .fields import AbsoluteMediaUrlField


class ComedianMinimalSerializer(serializers.ModelSerializer):
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "attributes", "image_url"]


class VideoMinimalSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()
    youtube_id = serializers.CharField(source="video_id")

    class Meta:
        model = Video
        fields = ["id", "slug", "number", "title", "youtube_id", "date", "guests"]

    def get_slug(self, video):
        return video_public_slug(video)

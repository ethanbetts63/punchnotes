from rest_framework import serializers

from pipeline.models import Comedian, Video
from api.set_slugs import set_public_slug
from api.video_slugs import video_public_slug
from .fields import AbsoluteMediaUrlField


class PublicSetSlugMixin(serializers.Serializer):
    slug = serializers.SerializerMethodField()

    def get_slug(self, set_obj):
        return set_public_slug(set_obj)


class PublicVideoSlugMixin(serializers.Serializer):
    slug = serializers.SerializerMethodField()

    def get_slug(self, video):
        return video_public_slug(video)


class ComedianMinimalSerializer(serializers.ModelSerializer):
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "attributes", "image_url"]


class VideoMinimalSerializer(PublicVideoSlugMixin, serializers.ModelSerializer):
    youtube_id = serializers.CharField(source="video_id")

    class Meta:
        model = Video
        fields = ["id", "slug", "number", "title", "youtube_id", "date", "guests"]

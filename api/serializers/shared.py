from rest_framework import serializers

from pipeline.models import Comedian, Video


class ComedianMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "attributes", "image_url"]


class VideoMinimalSerializer(serializers.ModelSerializer):
    youtube_id = serializers.CharField(source="video_id")

    class Meta:
        model = Video
        fields = ["id", "number", "title", "youtube_id", "date", "guests"]

from rest_framework import serializers

from pipeline.models import Comedian, Episode


class ComedianMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "attributes", "image_url"]


class EpisodeMinimalSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    youtube_id = serializers.CharField(source="video_id")
    date = serializers.DateField(source="published_at")
    guests = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Episode
        fields = ["id", "number", "title", "youtube_id", "date", "guests"]

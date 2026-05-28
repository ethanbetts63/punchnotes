from rest_framework import serializers

from pipeline.models import Comedian, Episode


class ComedianMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comedian
        fields = ["id", "name", "slug"]


class EpisodeMinimalSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(source="episode_number")
    title = serializers.CharField(source="episode_title")
    url = serializers.URLField(source="episode_url")
    date = serializers.DateField(source="published_at")

    class Meta:
        model = Episode
        fields = ["id", "number", "title", "url", "date"]

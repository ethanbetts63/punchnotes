from rest_framework import serializers

from pipeline.models import Comedian, Set
from .shared import EpisodeMinimalSerializer


class SetInComedianSerializer(serializers.ModelSerializer):
    episode = EpisodeMinimalSerializer()

    class Meta:
        model = Set
        fields = ["id", "set_number", "episode", "joke_book"]


class ComedianListSerializer(serializers.ModelSerializer):
    set_count = serializers.IntegerField()
    appearances = serializers.IntegerField()

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "comedian_type", "set_count", "appearances"]


class ComedianDetailSerializer(serializers.ModelSerializer):
    sets = SetInComedianSerializer(many=True)

    class Meta:
        model = Comedian
        fields = ["id", "name", "slug", "comedian_type", "sets"]

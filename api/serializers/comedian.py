import random
from collections import Counter

from rest_framework import serializers

from api.beat_utils import beat_display_lines
from pipeline.models import Comedian, Set
from .fields import AbsoluteMediaUrlField
from .shared import PublicSetSlugMixin, VideoMinimalSerializer


SAMPLE_JOKES_PER_SET = 2
SAMPLE_JOKE_SETUP_LINES = 3
SAMPLE_JOKE_TAGS = 2


def joke_excerpt(lines):
    """The setup lines just before the first punchline, the punchline, and the tags right after it."""
    punchline = next(i for i, line in enumerate(lines) if line["label"] == "punchline")
    end = punchline + 1
    while end < len(lines) and end - punchline <= SAMPLE_JOKE_TAGS and lines[end]["label"] == "tag":
        end += 1
    return lines[max(0, punchline - SAMPLE_JOKE_SETUP_LINES):end]


class SetInComedianSerializer(PublicSetSlugMixin, serializers.ModelSerializer):
    video = VideoMinimalSerializer()
    image_url = AbsoluteMediaUrlField()
    sample_jokes = serializers.SerializerMethodField()

    class Meta:
        model = Set
        fields = [
            "id", "slug", "video", "attributes",
            "start_seconds", "bit_count",
            "punch_density", "tag_density",
            "image_url", "image_capture_seconds",
            "sample_jokes",
        ]

    def get_sample_jokes(self, set_obj):
        """A few jokes from the set for the comedian page, chosen at random but seeded by the set so the page reads
        the same on every render. Only beats that land on a punchline count as a joke."""
        set_lines = list(set_obj.lines.all())
        jokes = []
        for bit in set_obj.bits.all():
            for beat in bit.beats.all():
                lines = beat_display_lines(beat, set_lines=set_lines)
                if any(line["label"] == "punchline" for line in lines):
                    jokes.append({
                        "beat_id": beat.beat_id,
                        "joke_type": beat.joke_type or "",
                        "lines": [
                            {"label": line["label"], "text": line["text"]}
                            for line in joke_excerpt(lines)
                        ],
                    })
        picked = random.Random(set_obj.pk).sample(range(len(jokes)), min(SAMPLE_JOKES_PER_SET, len(jokes)))
        return [jokes[i] for i in sorted(picked)]


class ComedianListSerializer(serializers.ModelSerializer):
    image_url = AbsoluteMediaUrlField()

    class Meta:
        model = Comedian
        fields = [
            "id", "name", "slug", "attributes",
            "image_url",
            "set_count",
            "has_small_joke_book", "has_medium_joke_book", "has_large_joke_book",
            "avg_punch_density", "avg_tag_density",
            "avg_bits_per_set", "avg_beats_per_set",
        ]


class ComedianDetailSerializer(ComedianListSerializer):
    sets = SetInComedianSerializer(many=True)
    joke_type_counts = serializers.SerializerMethodField()

    class Meta(ComedianListSerializer.Meta):
        fields = ComedianListSerializer.Meta.fields + ["sets", "joke_type_counts"]

    def get_joke_type_counts(self, comedian):
        """How often each joke mechanism turns up across every set, most used first."""
        counts = Counter(
            beat.joke_type
            for set_obj in comedian.sets.all()
            for bit in set_obj.bits.all()
            for beat in bit.beats.all()
            if beat.joke_type
        )
        return dict(counts.most_common())

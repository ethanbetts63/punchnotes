from django.db import models
from django.core.exceptions import ValidationError


ATTRIBUTE_VALUES = frozenset({
    'bucket_pull', 'regular', 'golden_ticket', 'special',
    'gay', 'lesbian', 'bisexual',
    'man', 'woman', 'trans',
    'white', 'black', 'asian', 'latino', 'middle_eastern',
    'disabled', 'old', 'young', 'middle-age',
})

APPEARANCE_ATTRIBUTES = frozenset({'bucket_pull', 'regular', 'golden_ticket', 'special'})


def validate_attributes(value):
    if not isinstance(value, list):
        raise ValidationError("Comedian attributes must be a list.")

    invalid = [
        item for item in value
        if not isinstance(item, str)
        or item not in ATTRIBUTE_VALUES
    ]
    if invalid:
        allowed = ", ".join(sorted(ATTRIBUTE_VALUES))
        raise ValidationError(
            f"Comedian attributes must use allowed values ({allowed})."
        )


class Comedian(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    attributes = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_attributes],
    )

    # Denormalised counts updated by refresh_comedian_stats
    joke_count = models.PositiveIntegerField(default=0)
    has_small_joke_book = models.BooleanField(default=False)
    has_medium_joke_book = models.BooleanField(default=False)
    has_large_joke_book = models.BooleanField(default=False)

    # Denormalised counts updated by refresh_comedian_stats
    set_count = models.PositiveSmallIntegerField(default=0)

    # Denormalised ratio averages updated by refresh_comedian_stats
    avg_hit_ratio = models.FloatField(null=True, blank=True)
    avg_tag_density = models.FloatField(null=True, blank=True)
    avg_bits_per_set = models.FloatField(null=True, blank=True)
    avg_beats_per_set = models.FloatField(null=True, blank=True)

    # Display image derived from the comedian's latest image-bearing set.
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    image_set = models.ForeignKey(
        'pipeline.Set',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
    )

    def __str__(self):
        return self.name

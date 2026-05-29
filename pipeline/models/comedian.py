from django.db import models
from django.core.exceptions import ValidationError


ATTRIBUTE_CHOICES = [
    ('bucket_pull', 'Bucket Pull'),
    ('regular', 'Regular'),
    ('golden_ticket', 'Golden Ticket'),
    ('special', 'Special'),
    ('gay', 'Gay'),
    ('lesbian', 'Lesbian'),
    ('bisexual', 'Bisexual'),
    ('man', 'Man'),
    ('woman', 'Woman'),
    ('trans', 'Trans'),
    ('white', 'White'),
    ('black', 'Black'),
    ('asian', 'Asian'),
    ('latino', 'Latino'),
    ('middle_eastern', 'Middle Eastern'),
    ('disabled', 'Disabled'),
    ('old', 'Old'),
    ('young', 'Young'),
    ('middle-age', 'Middle-Age'),
]

ATTRIBUTE_VALUES = {value for value, _label in ATTRIBUTE_CHOICES}


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

    # Denormalised ratio averages updated by refresh_comedian_stats
    avg_hit_ratio = models.FloatField(null=True, blank=True)
    avg_punchline_tag_ratio = models.FloatField(null=True, blank=True)
    avg_bits_per_set = models.FloatField(null=True, blank=True)
    avg_beats_per_set = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

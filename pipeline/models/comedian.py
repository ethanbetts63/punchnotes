from django.db import models


class Comedian(models.Model):
    COMEDIAN_TYPE_CHOICES = [
        ('bucket_pull', 'Bucket Pull'),
        ('regular', 'Regular'),
        ('golden_ticket', 'Golden Ticket'),
        ('special', 'Special'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    comedian_type = models.CharField(max_length=20, choices=COMEDIAN_TYPE_CHOICES, blank=True)
    comedian_attributes = models.JSONField(default=list, blank=True)

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

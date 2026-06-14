from django.core.exceptions import ValidationError
from django.db import models

SET_ATTRIBUTE_VALUES = {"small_joke_book", "medium_joke_book", "large_joke_book"}


def validate_set_attributes(value):
    if not isinstance(value, list):
        raise ValidationError("attributes must be a list")
    for item in value:
        if item not in SET_ATTRIBUTE_VALUES:
            raise ValidationError(f"Unknown set attribute: {item!r}")


class Set(models.Model):
    video = models.ForeignKey('pipeline.Video', on_delete=models.CASCADE, related_name='sets')
    comedian = models.ForeignKey('pipeline.Comedian', on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveSmallIntegerField()
    start_seconds = models.FloatField()
    interview_end_line = models.PositiveSmallIntegerField(blank=True, null=True)
    interview_end_seconds = models.FloatField(blank=True, null=True)
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    image_capture_seconds = models.FloatField(blank=True, null=True)
    attributes = models.JSONField(default=list, blank=True, validators=[validate_set_attributes])

    # Computed from lines and bits after import
    bit_count = models.PositiveSmallIntegerField(default=0)
    hit_ratio = models.FloatField(null=True, blank=True)
    tag_density = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['start_seconds']
        unique_together = [['video', 'set_number']]

    def __str__(self):
        return f"{self.video} – Set {self.set_number}: {self.comedian}"

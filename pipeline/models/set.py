from django.db import models


class Set(models.Model):
    episode = models.ForeignKey('pipeline.Episode', on_delete=models.CASCADE, related_name='sets')
    comedian = models.ForeignKey('pipeline.Comedian', on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveSmallIntegerField()
    start_seconds = models.FloatField()
    interview_end_line = models.PositiveSmallIntegerField(blank=True, null=True)
    interview_end_seconds = models.FloatField(blank=True, null=True)
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    image_capture_seconds = models.FloatField(blank=True, null=True)
    joke_book = models.CharField(
        max_length=10,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        blank=True,
        null=True,
    )

    # Computed from lines after import
    hit_ratio = models.FloatField(null=True, blank=True)
    punchline_tag_ratio = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['start_seconds']
        unique_together = [['episode', 'set_number']]

    def __str__(self):
        return f"{self.episode} – Set {self.set_number}: {self.comedian}"

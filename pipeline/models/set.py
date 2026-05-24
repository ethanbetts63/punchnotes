from django.db import models


class Set(models.Model):
    episode = models.ForeignKey('pipeline.Episode', on_delete=models.CASCADE, related_name='sets')
    comedian = models.ForeignKey('pipeline.Comedian', on_delete=models.CASCADE, related_name='sets')
    set_number = models.PositiveSmallIntegerField()
    start_seconds = models.FloatField()

    class Meta:
        ordering = ['set_number']
        unique_together = [['episode', 'set_number']]

    def __str__(self):
        return f"{self.episode} – Set {self.set_number}: {self.comedian}"

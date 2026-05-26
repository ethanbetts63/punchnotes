from django.db import models


class Beat(models.Model):
    bit = models.ForeignKey('pipeline.Bit', on_delete=models.CASCADE, related_name='beats')
    beat_id = models.CharField(max_length=50)
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()
    premise = models.TextField(null=True, blank=True)
    topics = models.JSONField(default=list)

    class Meta:
        ordering = ['line_start']
        unique_together = [['bit', 'beat_id']]

    def __str__(self):
        return f"{self.bit} – {self.beat_id}"

from django.db import models


class Bit(models.Model):
    set = models.ForeignKey('pipeline.Set', on_delete=models.CASCADE, related_name='bits')
    bit_id = models.CharField(max_length=50)
    premise = models.TextField(null=True, blank=True)
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['line_start']
        unique_together = [['set', 'bit_id']]

    def __str__(self):
        return f"{self.set} – {self.bit_id}"

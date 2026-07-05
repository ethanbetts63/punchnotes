from django.db import models


class BeatSegment(models.Model):
    beat = models.ForeignKey('pipeline.Beat', on_delete=models.CASCADE, related_name='segments')
    ordinal = models.PositiveSmallIntegerField()
    text = models.TextField()
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()
    embedding = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['beat', 'ordinal']
        unique_together = [['beat', 'ordinal']]

    def __str__(self):
        return f"{self.beat} â€“ segment {self.ordinal}"

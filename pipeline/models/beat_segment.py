from django.db import models


class BeatSegment(models.Model):
    beat = models.ForeignKey('pipeline.Beat', on_delete=models.CASCADE, related_name='segments')
    ordinal = models.PositiveSmallIntegerField()
    text = models.TextField()
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()
    # Dense little-endian float32 bytes; see pipeline.utils.vectors. Stored as a blob
    # rather than JSON because the text encoding is 5x the bytes and needs decoding
    # into millions of Python floats on every read.
    embedding = models.BinaryField(default=b"")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['beat', 'ordinal']
        unique_together = [['beat', 'ordinal']]

    def __str__(self):
        return f"{self.beat} â€“ segment {self.ordinal}"

from django.db import models


class Beat(models.Model):
    JOKE_TYPE_CHOICES = [
        ('misdirect', 'Misdirect'),
        ('reframe', 'Reframe'),
        ('phonetic-match', 'Phonetic match'),
        ('double-meaning', 'Double-meaning'),
        ('contradiction', 'Contradiction'),
        ('analogy', 'Analogy'),
        ('hyperbole', 'Hyperbole'),
        ('elephant-in-the-room', 'Elephant-in-the-room'),
        ('anti-humor', 'Anti-humor'),
    ]
    bit = models.ForeignKey('pipeline.Bit', on_delete=models.CASCADE, related_name='beats')
    beat_id = models.CharField(max_length=50)
    line_start = models.PositiveSmallIntegerField()
    line_end = models.PositiveSmallIntegerField()
    premise = models.TextField(null=True, blank=True)
    joke_type = models.CharField(max_length=30, choices=JOKE_TYPE_CHOICES, null=True, blank=True)
    keys = models.JSONField(default=list)
    key_embeddings = models.JSONField(default=list)
    premise_embedding = models.JSONField(default=list)

    class Meta:
        ordering = ['line_start']
        unique_together = [['bit', 'beat_id']]

    def __str__(self):
        return f"{self.bit} – {self.beat_id}"

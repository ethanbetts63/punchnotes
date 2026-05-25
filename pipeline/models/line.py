from django.db import models


class Line(models.Model):
    LABEL_CHOICES = [
        ('setup', 'Setup'),
        ('punchline', 'Punchline'),
        ('tag', 'Tag'),
        ('fluff', 'Fluff'),
    ]
    set = models.ForeignKey('pipeline.Set', on_delete=models.CASCADE, related_name='lines')
    line_number = models.PositiveSmallIntegerField()
    label = models.CharField(max_length=20, choices=LABEL_CHOICES)
    text = models.TextField()
    start_seconds = models.FloatField()

    class Meta:
        ordering = ['line_number']
        unique_together = [['set', 'line_number']]

    def __str__(self):
        return f"Set {self.set_id} – Line {self.line_number} ({self.label})"

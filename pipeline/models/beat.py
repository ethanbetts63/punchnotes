from django.db import models


class Beat(models.Model):
    BEAT_TYPE_CHOICES = [
        ('premise', 'Premise'),
        ('punchline', 'Punchline'),
        ('tag', 'Tag'),
        ('act_out', 'Act Out'),
        ('crowd_work', 'Crowd Work'),
        ('transition', 'Transition'),
    ]
    set = models.ForeignKey('pipeline.Set', on_delete=models.CASCADE, related_name='beats')
    beat_number = models.PositiveSmallIntegerField()
    beat_type = models.CharField(max_length=20, choices=BEAT_TYPE_CHOICES)
    text = models.TextField()
    start_seconds = models.FloatField()

    class Meta:
        ordering = ['beat_number']
        unique_together = [['set', 'beat_number']]

    def __str__(self):
        return f"Set {self.set_id} – Beat {self.beat_number} ({self.beat_type})"

from django.db import models


class Episode(models.Model):
    video_id = models.CharField(max_length=20, unique=True)
    episode_title = models.CharField(max_length=500)
    episode_url = models.URLField()
    published_at = models.DateField(null=True, blank=True)
    guests = models.ManyToManyField('pipeline.Comedian', related_name='guest_appearances', blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.episode_title

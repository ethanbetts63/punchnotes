from django.db import models


class Video(models.Model):
    video_id = models.CharField(max_length=20, unique=True)
    number = models.PositiveSmallIntegerField(null=True, blank=True, db_index=True)
    title = models.CharField(max_length=500)
    url = models.URLField()
    date = models.DateField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    guests = models.JSONField(default=list, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    view_count = models.PositiveBigIntegerField(null=True, blank=True)
    like_count = models.PositiveBigIntegerField(null=True, blank=True)
    comment_count = models.PositiveBigIntegerField(null=True, blank=True)
    tags = models.JSONField(null=True, blank=True)

    # Denormalised counts updated by import_lines after each set is imported
    set_count = models.PositiveSmallIntegerField(default=0)
    bucket_pull_count = models.PositiveSmallIntegerField(default=0)
    golden_ticket_count = models.PositiveSmallIntegerField(default=0)
    regular_count = models.PositiveSmallIntegerField(default=0)
    large_joke_book_count = models.PositiveSmallIntegerField(default=0)

    # Denormalised engagement ratio updated by video metadata imports
    view_like_ratio = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-number']

    def __str__(self):
        return self.title

from django.db import models


class Comedian(models.Model):
    COMEDIAN_TYPE_CHOICES = [
        ('bucket_pull', 'Bucket Pull'),
        ('regular', 'Regular'),
        ('golden_ticket', 'Golden Ticket'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    comedian_type = models.CharField(max_length=20, choices=COMEDIAN_TYPE_CHOICES, blank=True)

    def __str__(self):
        return self.name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0001_initial"),
    ]

    operations = [
        # Set ratio fields
        migrations.AddField(
            model_name="set",
            name="hit_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="set",
            name="punchline_tag_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        # Comedian stat fields
        migrations.AddField(
            model_name="comedian",
            name="joke_count",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="comedian",
            name="has_small_joke_book",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="comedian",
            name="has_medium_joke_book",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="comedian",
            name="has_large_joke_book",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="comedian",
            name="avg_hit_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="comedian",
            name="avg_punchline_tag_ratio",
            field=models.FloatField(blank=True, null=True),
        ),
        # Update comedian_type choices to include 'special'
        migrations.AlterField(
            model_name="comedian",
            name="comedian_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("bucket_pull", "Bucket Pull"),
                    ("regular", "Regular"),
                    ("golden_ticket", "Golden Ticket"),
                    ("special", "Special"),
                ],
                max_length=20,
            ),
        ),
    ]

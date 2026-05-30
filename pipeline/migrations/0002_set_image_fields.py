from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="set",
            name="image_url",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="set",
            name="image_capture_seconds",
            field=models.FloatField(blank=True, null=True),
        ),
    ]

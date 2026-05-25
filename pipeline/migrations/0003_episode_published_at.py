from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0002_remove_line_confidence"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="published_at",
            field=models.DateField(blank=True, null=True),
        ),
    ]

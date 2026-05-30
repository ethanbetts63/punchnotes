from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0002_set_image_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="comedian",
            name="image_url",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AddField(
            model_name="comedian",
            name="image_set",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="pipeline.set",
            ),
        ),
    ]

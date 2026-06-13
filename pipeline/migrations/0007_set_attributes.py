from django.db import migrations, models
import pipeline.models.set


def migrate_joke_book_to_attributes(apps, schema_editor):
    Set = apps.get_model("pipeline", "Set")
    mapping = {"small": "small_joke_book", "medium": "medium_joke_book", "large": "large_joke_book"}
    for set_obj in Set.objects.exclude(joke_book=None).exclude(joke_book=""):
        attr = mapping.get(set_obj.joke_book)
        if attr:
            set_obj.attributes = [attr]
            set_obj.save(update_fields=["attributes"])


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0006_remove_beat_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="set",
            name="attributes",
            field=models.JSONField(blank=True, default=list, validators=[pipeline.models.set.validate_set_attributes]),
        ),
        migrations.RunPython(migrate_joke_book_to_attributes, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="set",
            name="joke_book",
        ),
    ]

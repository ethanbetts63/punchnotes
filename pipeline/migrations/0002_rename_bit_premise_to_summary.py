from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bit",
            old_name="premise",
            new_name="summary",
        ),
    ]

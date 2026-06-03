from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0003_alter_beat_joke_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beat',
            old_name='topics',
            new_name='keys',
        ),
        migrations.AddField(
            model_name='beat',
            name='key_embeddings',
            field=models.JSONField(default=list),
        ),
    ]

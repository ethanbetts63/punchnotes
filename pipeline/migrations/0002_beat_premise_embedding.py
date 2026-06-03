from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='beat',
            name='premise_embedding',
            field=models.JSONField(default=list),
        ),
    ]

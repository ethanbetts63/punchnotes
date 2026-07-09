"""Convert BeatSegment.embedding from JSONField to BinaryField.

The vectors are float32. As JSON text each 768-dim row costs ~15.8 KB instead of
3 KB, so the table ships ~330 MB over the wire instead of ~63 MB and every read
builds ~15.7M throwaway Python floats.

Converted in id-ordered chunks: reading the whole JSON column at once is the very
thing this migration exists to stop doing, and it is what makes the report run out
of memory on small servers.
"""

from django.db import migrations, models


CHUNK_SIZE = 500


def _convert(apps, schema_editor, source: str, dest: str, transform):
    BeatSegment = apps.get_model("pipeline", "BeatSegment")
    rows = BeatSegment.objects.using(schema_editor.connection.alias)

    total = rows.count()
    if not total:
        return

    done = 0
    after_id = 0
    while True:
        chunk = list(
            rows.filter(id__gt=after_id).order_by("id").values_list("id", source)[:CHUNK_SIZE]
        )
        if not chunk:
            break

        rows.bulk_update(
            [BeatSegment(id=pk, **{dest: transform(value)}) for pk, value in chunk],
            [dest],
            batch_size=CHUNK_SIZE,
        )
        after_id = chunk[-1][0]
        done += len(chunk)
        print(f"  {done:,}/{total:,} segments converted", flush=True)


def to_binary(apps, schema_editor):
    from pipeline.utils.vectors import pack_embedding

    _convert(apps, schema_editor, "embedding", "embedding_bin", pack_embedding)


def to_json(apps, schema_editor):
    from pipeline.utils.vectors import unpack_embedding

    _convert(apps, schema_editor, "embedding_bin", "embedding", lambda blob: unpack_embedding(blob).tolist())


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0002_remove_beat_embedding"),
    ]

    operations = [
        migrations.AddField(
            model_name="beatsegment",
            name="embedding_bin",
            field=models.BinaryField(default=b""),
        ),
        migrations.RunPython(to_binary, to_json),
        migrations.RemoveField(model_name="beatsegment", name="embedding"),
        migrations.RenameField(
            model_name="beatsegment",
            old_name="embedding_bin",
            new_name="embedding",
        ),
    ]

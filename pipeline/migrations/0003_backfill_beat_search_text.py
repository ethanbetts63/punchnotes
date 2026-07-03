from django.db import migrations

SEARCHABLE_BEAT_LINE_LABELS = ("setup", "punchline", "tag")


def backfill_search_text(apps, schema_editor):
    Beat = apps.get_model("pipeline", "Beat")
    Line = apps.get_model("pipeline", "Line")

    beats = list(Beat.objects.select_related("bit").only("id", "line_start", "line_end", "bit__set_id"))
    set_ids = {beat.bit.set_id for beat in beats}

    lines_by_set = {}
    lines = (
        Line.objects.filter(set_id__in=set_ids, label__in=SEARCHABLE_BEAT_LINE_LABELS)
        .order_by("set_id", "line_number")
        .only("set_id", "line_number", "text")
    )
    for line in lines:
        lines_by_set.setdefault(line.set_id, []).append(line)

    updated = []
    for beat in beats:
        set_id = beat.bit.set_id
        texts = [
            line.text
            for line in lines_by_set.get(set_id, [])
            if beat.line_start <= line.line_number <= beat.line_end
        ]
        beat.search_text = " ".join(texts)
        updated.append(beat)

    Beat.objects.bulk_update(updated, ["search_text"], batch_size=500)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pipeline", "0002_beat_search_text"),
    ]

    operations = [
        migrations.RunPython(backfill_search_text, noop),
    ]

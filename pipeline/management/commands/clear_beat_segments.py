# Server-side: delete every BeatSegment row so the next segment-embedding run
# rebuilds them from scratch. Needed after any change to how segments are built
# (e.g. excluding fluff lines), because ensure_beat_segments() skips beats that
# already have segments -- clearing only the embeddings would keep the stale text.
#
# After running this on the server, regenerate as usual:
#   (local)  python manage.py generate --segment_embeddings
#   (local)  python manage.py upload   --segment_embeddings
#   (server) python manage.py update   --segment_embeddings

from django.core.management.base import BaseCommand

from pipeline.log import Log
from pipeline.models import BeatSegment


class Command(BaseCommand):
    help = "Delete all beat segments so they are rebuilt on the next segment-embedding run."

    def handle(self, *args, **options):
        log = Log(self.stdout, self.style)

        count = BeatSegment.objects.count()
        if count == 0:
            log("No beat segments to delete.")
            return

        BeatSegment.objects.all().delete()
        log.success(
            f"Deleted {count} beat segment(s). "
            f"Run `generate --segment_embeddings` to rebuild and re-embed them."
        )

from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Server-side: ingest pipeline data from inbox dirs into the database"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--ep_meta", action="store_true", help="Import episode metadata from ep_meta_inbox/")
        group.add_argument("--comedian_aliases", action="store_true", help="Apply comedian alias relationships and dedup DB")
        group.add_argument("--set_images", action="store_true", help="Import set images from set_images_inbox/")
        group.add_argument("--embeddings", action="store_true", help="Write embeddings from embeddings_inbox/ to DB")

    def handle(self, *args, **options):
        log = Log(self.stdout, self.style)

        if options["ep_meta"]:
            from pipeline.server_utils.ep_meta import run_update_ep_meta
            run_update_ep_meta(log)

        elif options["comedian_aliases"]:
            from pipeline.server_utils.comedian_aliases import run_update_comedian_aliases
            run_update_comedian_aliases(log)

        elif options["set_images"]:
            from pipeline.server_utils.set_images import run_update_set_images
            run_update_set_images(log)

        elif options["embeddings"]:
            from pipeline.server_utils.embeddings import run_update_embeddings
            run_update_embeddings(log)

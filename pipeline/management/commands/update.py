from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Server-side: ingest pipeline data from inbox dirs into the database"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--annotated", action="store_true", help="Import annotated sets from annotated_set_inbox/ into DB")
        group.add_argument("--ep_meta", action="store_true", help="Import episode metadata from kt_ep_archive.jsonl")
        group.add_argument("--comedian_aliases", action="store_true", help="Apply comedian alias relationships and dedup DB")
        group.add_argument("--set_images", action="store_true", help="Import set images from set_images_inbox/ (or set_images_archive/ with --archive)")
        group.add_argument("--embeddings", action="store_true", help="Write embeddings from embeddings_inbox/ to DB")

        parser.add_argument("--archive", action="store_true", help="(--annotated) Read from bit_annotated_set_archive/ instead of inbox")

    def handle(self, *args, **options):
        log = Log(self.stdout, self.style)

        if options["annotated"]:
            from pipeline.utils.update.annotated_archive import run_update_annotated
            run_update_annotated(log, archive=options["archive"])

        elif options["ep_meta"]:
            from pipeline.utils.update.ep_meta import run_update_ep_meta
            run_update_ep_meta(log)

        elif options["comedian_aliases"]:
            from pipeline.utils.update.comedian_aliases import run_update_comedian_aliases
            run_update_comedian_aliases(log)

        elif options["set_images"]:
            from pipeline.utils.update.set_images import run_update_set_images
            run_update_set_images(log, archive=options["archive"])

        elif options["embeddings"]:
            from pipeline.utils.update.embeddings import run_update_embeddings
            run_update_embeddings(log, archive=options["archive"])

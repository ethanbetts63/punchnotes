from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Upload local pipeline data to the server"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--annotated", action="store_true", help="Upload annotated set JSON(s) to server (ingests immediately)")
        group.add_argument("--ep_meta", action="store_true", help="Upload episode metadata JSONL from ep_meta_outbox/")
        group.add_argument("--comedian_aliases", action="store_true", help="Upload comedian_name_relationships.json to server")
        group.add_argument("--set_images", action="store_true", help="Upload set images from set_images_outbox/")
        group.add_argument("--embeddings", action="store_true", help="Upload embedding JSONL from embeddings_outbox/")

        source = parser.add_mutually_exclusive_group()
        source.add_argument("--file", help="(--annotated) Upload a single JSON file from any path")
        source.add_argument("--dir", help="(--annotated) Upload all JSON files in a directory")

    def handle(self, *args, **options):
        log = Log(self.stdout, self.style)

        if options["annotated"]:
            from pipeline.local_utils.annotated import upload_annotated
            upload_annotated(options, log)

        elif options["ep_meta"]:
            from pipeline.local_utils.ep_meta import upload_ep_meta
            upload_ep_meta(options, log)

        elif options["comedian_aliases"]:
            from pipeline.local_utils.comedian_aliases import upload_comedian_aliases
            upload_comedian_aliases(log)

        elif options["set_images"]:
            from pipeline.local_utils.set_images import upload_set_images
            upload_set_images(options, log)

        elif options["embeddings"]:
            from pipeline.local_utils.embeddings import upload_embeddings
            upload_embeddings(options, log)

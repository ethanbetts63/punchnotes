from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Upload local pipeline data to the server"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--annotated", action="store_true", help="Upload annotated set JSON(s) to server (ingests immediately)")
        group.add_argument("--comedian_aliases", action="store_true", help="Upload comedian_name_relationships.json to server")
        group.add_argument("--set_images", action="store_true", help="Upload set images from set_images_outbox/")
        group.add_argument("--embeddings", action="store_true", help="Upload embedding JSONL from embeddings_outbox/")
        group.add_argument("--segment_embeddings", action="store_true", help="Upload segment embedding JSONL from segment_embeddings_outbox/")

        source = parser.add_mutually_exclusive_group()
        source.add_argument("--file", help="(--annotated) Upload a single JSON file from any path")
        source.add_argument("--dir", help="(--annotated) Upload all JSON files in a directory")
        parser.add_argument("--archive", action="store_true", help="Upload from archive instead of outbox when supported")
        parser.add_argument("--local", action="store_true", help="Target local dev server (http://localhost:8000)")

    def handle(self, *args, **options):
        if options["local"]:
            from django.conf import settings
            settings.SERVER_BASE_URL = settings.LOCAL_SERVER_URL
        log = Log(self.stdout, self.style)

        if options["annotated"]:
            from pipeline.utils.upload.annotated import upload_annotated
            upload_annotated(options, log)

        elif options["comedian_aliases"]:
            from pipeline.utils.upload.comedian_aliases import upload_comedian_aliases
            upload_comedian_aliases(log)

        elif options["set_images"]:
            from pipeline.utils.upload.set_images import upload_set_images
            upload_set_images(options, log)

        elif options["embeddings"]:
            from pipeline.utils.upload.embeddings import upload_embeddings
            upload_embeddings(options, log)

        elif options["segment_embeddings"]:
            from pipeline.utils.upload.segment_embeddings import upload_segment_embeddings
            upload_segment_embeddings(options, log)

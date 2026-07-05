from django.core.management.base import BaseCommand

from pipeline.log import Log
from pipeline.utils.generate.embeddings_report import generate_embeddings_report


class Command(BaseCommand):
    help = "Generate joke similarity report from stored embeddings"

    def handle(self, *args, **options):
        generate_embeddings_report(Log(self.stdout, self.style))

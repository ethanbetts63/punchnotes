from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = "Delete archive images whose comedian slug does not match the set in the DB"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be deleted without removing any files",
        )

    def handle(self, *args, **options):
        from pipeline.utils.fix.set_image_archive import fix_set_image_archive
        log = Log(self.stdout, self.style)
        fix_set_image_archive(log, dry_run=options["dry_run"])

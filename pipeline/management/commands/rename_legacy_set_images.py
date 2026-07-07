from django.core.management.base import BaseCommand

from pipeline.log import Log


class Command(BaseCommand):
    help = (
        "One-time backfill: rename set-image files from the old "
        "KT{ep}_set{NN}_{slug} scheme to the new KT{ep}_{start_seconds}_{slug} "
        "scheme and update Set.image_url to match. Pure rename, no re-scraping."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be renamed without touching any files or the DB",
        )

    def handle(self, *args, **options):
        from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images
        log = Log(self.stdout, self.style)
        rename_legacy_set_images(log, dry_run=options["dry_run"])

# Local dev (default): squashes migrations and rebuilds the local DB from local archives.
# Server (--server): pulls latest code, reuses the already-committed migrations (no
# makemigrations), pulls the private archive, and reimports from it. Clears set-image
# files/DB fields instead of relinking from the archive, ready for a fresh local scrape
# via generate/upload/update --set_images (that scrape step still has to run locally).

import shutil
import subprocess

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Drop all tables, wipe migrations, rebuild schema, then reload base fixtures"

    def add_arguments(self, parser):
        parser.add_argument(
            "--server",
            action="store_true",
            help="Run the server-side variant instead of the local dev-only migration squash.",
        )

    def handle(self, *args, **options):
        server = options["server"]
        base_dir = settings.BASE_DIR

        if server:
            self.stdout.write("Pulling latest app code...")
            self._run_git(["git", "pull"], cwd=base_dir)

        # Drop all tables so migrate can recreate them cleanly
        self.stdout.write("Dropping all tables...")
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            tables = connection.introspection.table_names(cursor)
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                self.stdout.write(f"  Dropped: {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        if not server:
            # Delete migration files (keep __init__.py) -- local squash only;
            # the server always reuses whatever migrations are already committed.
            migrations_dir = base_dir / "pipeline" / "migrations"
            for f in migrations_dir.glob("*.py"):
                if f.name != "__init__.py":
                    f.unlink()
                    self.stdout.write(f"Deleted migration: {f.name}")

            # Clear __pycache__ directories
            for cache_dir in base_dir.rglob("__pycache__"):
                if "venv" in cache_dir.parts:
                    continue
                shutil.rmtree(cache_dir)
                self.stdout.write(f"Cleared cache: {cache_dir.relative_to(base_dir)}")

            self.stdout.write("\nRunning makemigrations...")
            call_command("makemigrations")

        self.stdout.write("\nRunning migrate...")
        call_command("migrate")

        data_dir = settings.PIPELINE_DATA_DIR
        private_dir = settings.PIPELINE_PRIVATE_DATA_DIR

        if server:
            self.stdout.write("\nPulling private archive...")
            call_command("archive", pull=True)

        kt_ep_archive = data_dir / "kt_ep_archive.jsonl"
        if kt_ep_archive.exists():
            self.stdout.write("\nImporting episode metadata from archive...")
            call_command("update", ep_meta=True)
        else:
            self.stdout.write(self.style.WARNING("\nNo kt_ep_archive.jsonl found; skipping episode import."))

        # Re-import all archived sets after videos exist.
        sets_archive = private_dir / "bit_annotated_set_archive"
        if sets_archive.exists() and any(sets_archive.glob("*.json")):
            self.stdout.write("\nImporting sets from archive...")
            call_command("update", annotated=True, archive=True)
        else:
            self.stdout.write("\nNo archived sets to import.")

        if server:
            self.stdout.write("\nApplying comedian aliases...")
            call_command("update", comedian_aliases=True)

        # Wipe public set-images so stale files don't accumulate across resets
        public_images_dir = settings.MEDIA_ROOT / "set-images"
        if public_images_dir.exists():
            self.stdout.write("\nWiping public set-images directory...")
            shutil.rmtree(public_images_dir)
        public_images_dir.mkdir(parents=True, exist_ok=True)

        if server:
            # Fresh-scrape prep: clearing image_url is what makes missing_image_sets()
            # (pipeline/utils/update/set_images.py) pick these back up for rescraping.
            self.stdout.write("\nClearing image references for a fresh scrape...")
            from pipeline.models import Comedian, Set
            Set.objects.update(image_url=None, image_capture_seconds=None)
            Comedian.objects.update(image_url=None, image_set=None)
            self.stdout.write("  Run generate/upload/update --set_images locally to rescrape images.")
        else:
            # Re-copy set images from archive and repopulate DB image_url fields
            images_archive = data_dir / "set_images_archive"
            image_exts = {".jpg", ".jpeg", ".png", ".webp"}
            if images_archive.exists() and any(p.suffix.lower() in image_exts for p in images_archive.iterdir()):
                self.stdout.write("\nRe-linking set images from archive...")
                call_command("update", set_images=True, archive=True)
            else:
                self.stdout.write("\nNo archived set images to re-link.")

        if not server:
            segment_embeddings_archive = private_dir / "segment_embeddings_archive"
            if segment_embeddings_archive.exists() and any(segment_embeddings_archive.glob("*.jsonl")):
                self.stdout.write("\nRestoring segment embeddings from archive...")
                call_command("update", segment_embeddings=True, archive=True)
            else:
                self.stdout.write("\nNo archived segment embeddings to restore.")

        self.stdout.write(self.style.SUCCESS("\nDatabase reset complete."))

    def _run_git(self, cmd, cwd):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.stdout.strip():
            self.stdout.write(result.stdout.strip())
        if result.returncode != 0:
            raise CommandError(result.stderr.strip() or f"Command failed: {' '.join(cmd)}")

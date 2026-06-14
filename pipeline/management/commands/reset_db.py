import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Drop all tables, wipe migrations, rebuild schema, then reload base fixtures"

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR

        # Drop all tables so the fresh migration can recreate them cleanly
        self.stdout.write("Dropping all tables...")
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            tables = connection.introspection.table_names(cursor)
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                self.stdout.write(f"  Dropped: {table}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Delete migration files (keep __init__.py)
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

        # Load base fixtures (episodes are imported from scraped JSONL below)
        fixtures_dir = base_dir / "data" / "fixtures"
        fixtures = sorted(fixtures_dir.glob("*.json"))
        if fixtures:
            for fixture in fixtures:
                self.stdout.write(f"\nLoading fixture: {fixture.name}...")
                call_command("loaddata", str(fixture))

        # Re-import all archived sets
        data_dir = settings.PIPELINE_DATA_DIR
        sets_archive = data_dir / "bit_annotated_set_archive"
        if sets_archive.exists() and any(sets_archive.glob("*.json")):
            self.stdout.write("\nImporting sets from archive...")
            call_command("import_sets", archive=True)
        else:
            self.stdout.write("\nNo archived sets to import.")

        # Wipe public set-images so stale files don't accumulate across resets
        public_images_dir = settings.BASE_DIR / "frontend" / "public" / "set-images"
        if public_images_dir.exists():
            self.stdout.write("\nWiping public set-images directory...")
            shutil.rmtree(public_images_dir)
            public_images_dir.mkdir()

        # Re-copy set images from archive and repopulate DB image_url fields
        images_archive = data_dir / "set_images_archive"
        image_exts = {".jpg", ".jpeg", ".png", ".webp"}
        if images_archive.exists() and any(p.suffix.lower() in image_exts for p in images_archive.iterdir()):
            self.stdout.write("\nRe-linking set images from archive...")
            call_command("import_set_images", source_dir=str(images_archive), replace=True)
        else:
            self.stdout.write("\nNo archived set images to re-link.")

        full_episode_jsonl = settings.PIPELINE_DATA_DIR / "full_kt_episodes.jsonl"
        basic_episode_jsonl = settings.PIPELINE_DATA_DIR / "basic_kt_episodes.jsonl"
        if full_episode_jsonl.exists():
            self.stdout.write("\nImporting full episode metadata...")
            call_command("import_episodes_jsonl", str(full_episode_jsonl))
        elif basic_episode_jsonl.exists():
            self.stdout.write("\nImporting basic episode metadata...")
            call_command("import_episodes_jsonl", str(basic_episode_jsonl))
        else:
            self.stdout.write(self.style.WARNING("\nNo episode JSONL found; skipping episode import."))

        self.stdout.write(self.style.SUCCESS("\nDatabase reset complete."))

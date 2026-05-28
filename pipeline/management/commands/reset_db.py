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

        # Load base fixtures (episodes are populated via fetch_episodes, not fixtures)
        fixtures_dir = base_dir / "data" / "fixtures"
        fixtures = sorted(fixtures_dir.glob("*.json"))
        if fixtures:
            for fixture in fixtures:
                self.stdout.write(f"\nLoading fixture: {fixture.name}...")
                call_command("loaddata", str(fixture))

        # Re-import all archived sets
        archive_dir = base_dir / "data" / "bit_annotated_set_archive"
        if archive_dir.exists() and any(archive_dir.glob("*.json")):
            self.stdout.write("\nImporting sets from archive...")
            call_command("import_sets", source_dir=str(archive_dir))
        else:
            self.stdout.write("\nNo archived sets to import.")

        self.stdout.write("\nFetching episodes from YouTube playlist...")
        call_command("fetch_episodes")

        self.stdout.write(self.style.SUCCESS("\nDatabase reset complete."))

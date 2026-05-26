import shutil
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Wipe the database, delete all migrations, clear caches, then rebuild from scratch"

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR

        # Delete the SQLite database
        db_path = base_dir / "db.sqlite3"
        if db_path.exists():
            db_path.unlink()
            self.stdout.write("Deleted db.sqlite3")

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

        # Rebuild
        self.stdout.write("\nRunning makemigrations...")
        call_command("makemigrations")

        self.stdout.write("\nRunning migrate...")
        call_command("migrate")

        self.stdout.write(self.style.SUCCESS("\nDatabase reset complete."))

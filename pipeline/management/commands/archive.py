import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Sync the private archive repo (--push or --pull)"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--push", action="store_true", help="Commit and push archive changes to private repo")
        group.add_argument("--pull", action="store_true", help="Pull latest archive from private repo")

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_PRIVATE_DATA_DIR

        def run(cmd):
            result = subprocess.run(cmd, cwd=data_dir, capture_output=True, text=True)
            if result.stdout.strip():
                self.stdout.write(result.stdout.strip())
            if result.returncode != 0:
                raise CommandError(result.stderr.strip() or f"Command failed: {' '.join(cmd)}")

        if options["pull"]:
            run(["git", "pull"])
            self.stdout.write(self.style.SUCCESS("Archive pulled."))
            return

        run(["git", "add", "transcript_archive", "bit_annotated_set_archive"])

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=data_dir, capture_output=True, text=True
        )
        if not status.stdout.strip():
            self.stdout.write("Nothing to commit.")
            return

        run(["git", "commit", "-m", "update archive"])
        run(["git", "push"])
        self.stdout.write(self.style.SUCCESS("Archive pushed."))

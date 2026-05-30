import json
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from pipeline.models import Set


IMAGE_NAME_RE = re.compile(
    r"^KT(?P<episode_number>\d+)_(?:set(?P<padded_set_number>\d+)|(?P<set_number>\d+))_"
    r"(?P<comic_slug>[a-z0-9][a-z0-9_-]*)\.(?P<ext>jpe?g|png|webp)$",
    re.IGNORECASE,
)


def metadata_path(image_path):
    return image_path.with_suffix(image_path.suffix + ".json")


def read_metadata(image_path):
    path = metadata_path(image_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_image_name(path):
    match = IMAGE_NAME_RE.match(path.name)
    if not match:
        raise CommandError(
            f"Invalid image filename: {path.name}. Expected KT753_set01_yachao-yong.jpg "
            "or KT753_1_yachao-yong.jpg."
        )

    set_number = match.group("padded_set_number") or match.group("set_number")
    return {
        "episode_number": int(match.group("episode_number")),
        "set_number": int(set_number),
        "comic_slug": match.group("comic_slug").lower().replace("_", "-"),
    }


def public_image_url(filename):
    return f"/set-images/{filename}"


class Command(BaseCommand):
    help = "Import accepted set images from pipeline/data/4_set_images_inbox into the Set table."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            dest="source_dir",
            default=None,
            help="Directory to import from. Defaults to pipeline/data/4_set_images_inbox/.",
        )
        parser.add_argument(
            "--public-dir",
            default=None,
            help="Public image directory. Defaults to frontend/public/set-images/.",
        )
        parser.add_argument(
            "--archive-dir",
            default=None,
            help="Archive directory. Defaults to pipeline/data/set_images_archive/.",
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Replace existing Set image_url values and public files.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without writing files or updating the database.",
        )

    def handle(self, *args, **options):
        data_dir = settings.PIPELINE_DATA_DIR
        source_dir = Path(options["source_dir"]) if options["source_dir"] else data_dir / "4_set_images_inbox"
        public_dir = Path(options["public_dir"]) if options["public_dir"] else settings.BASE_DIR / "frontend" / "public" / "set-images"
        archive_dir = Path(options["archive_dir"]) if options["archive_dir"] else data_dir / "set_images_archive"

        files = sorted(
            path for path in source_dir.glob("*")
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )
        if not files:
            self.stdout.write(f"No image files found in {source_dir}")
            return

        if not options["dry_run"]:
            public_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.mkdir(parents=True, exist_ok=True)

        imported = skipped = failed = 0
        for image_path in files:
            try:
                result = self.import_image(
                    image_path=image_path,
                    public_dir=public_dir,
                    archive_dir=archive_dir,
                    replace=options["replace"],
                    dry_run=options["dry_run"],
                )
            except Exception as exc:
                failed += 1
                self.stdout.write(self.style.ERROR(f"Failed {image_path.name}: {exc}"))
                continue

            if result == "imported":
                imported += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {imported} imported, {skipped} skipped, {failed} failed."
            )
        )

    def import_image(self, image_path, public_dir, archive_dir, replace, dry_run):
        parsed = parse_image_name(image_path)
        set_obj = Set.objects.select_related("episode", "comedian").get(
            episode__episode_number=parsed["episode_number"],
            set_number=parsed["set_number"],
        )

        if set_obj.comedian.slug != parsed["comic_slug"]:
            self.stdout.write(
                self.style.WARNING(
                    f"{image_path.name}: filename comic slug '{parsed['comic_slug']}' does not match "
                    f"set comic '{set_obj.comedian.slug}'. Importing by episode/set number."
                )
            )

        if set_obj.image_url and not replace:
            self.stdout.write(f"Skipping {image_path.name}: Set already has image_url={set_obj.image_url}")
            return "skipped"

        public_path = public_dir / image_path.name
        if public_path.exists() and not replace:
            self.stdout.write(f"Skipping {image_path.name}: public file already exists")
            return "skipped"

        metadata = read_metadata(image_path)
        capture_seconds = metadata.get("capture_seconds")
        image_url = public_image_url(image_path.name)

        self.stdout.write(
            f"{'Would import' if dry_run else 'Importing'} {image_path.name} -> "
            f"KT{set_obj.episode.episode_number} set {set_obj.set_number} ({set_obj.comedian.name})"
        )

        if dry_run:
            return "imported"

        with transaction.atomic():
            shutil.copy2(image_path, public_path)
            set_obj.image_url = image_url
            set_obj.image_capture_seconds = capture_seconds
            set_obj.save(update_fields=["image_url", "image_capture_seconds"])

            shutil.move(str(image_path), archive_dir / image_path.name)
            sidecar = metadata_path(image_path)
            if sidecar.exists():
                shutil.move(str(sidecar), archive_dir / sidecar.name)

        return "imported"

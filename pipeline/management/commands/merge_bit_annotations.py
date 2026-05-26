import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Merge bit annotations into annotated set files and write to 4_bit_annotated_set_inbox"

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        annotated_dir = data_dir / "3_annotated_set_inbox"
        bits_dir = data_dir / "bit_annotation_inbox"
        out_dir = data_dir / "4_bit_annotated_set_inbox"
        out_dir.mkdir(exist_ok=True)

        annotated_files = sorted(annotated_dir.glob("*.json"))
        if not annotated_files:
            self.stdout.write("No files in 3_annotated_set_inbox.")
            return

        merged = 0
        skipped = 0
        for set_path in annotated_files:
            bits_path = bits_dir / set_path.name
            if not bits_path.exists():
                self.stdout.write(self.style.WARNING(f"  [{set_path.name}] no matching bit annotation — skipped"))
                skipped += 1
                continue

            set_doc = json.loads(set_path.read_text(encoding="utf-8-sig"))
            bits_doc = json.loads(bits_path.read_text(encoding="utf-8-sig"))

            # Insert bits before lines
            lines = set_doc.pop("lines")
            set_doc["bits"] = bits_doc["bits"]
            set_doc["lines"] = lines

            out_path = out_dir / set_path.name
            out_path.write_text(json.dumps(set_doc, ensure_ascii=False, indent=2), encoding="utf-8")
            self.stdout.write(f"  [{set_path.name}] merged")
            merged += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone. {merged} merged, {skipped} skipped."))

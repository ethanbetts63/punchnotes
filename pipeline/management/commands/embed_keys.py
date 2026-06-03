from django.core.management.base import BaseCommand

from pipeline.models import Beat


MODEL_NAME = "all-mpnet-base-v2"


class Command(BaseCommand):
    help = "Compute and store key embeddings for beats that have keys but no embeddings"

    def handle(self, *args, **options):
        beats = list(Beat.objects.exclude(keys=[]).filter(key_embeddings=[]))
        count = len(beats)
        if not count:
            self.stdout.write("No beats need embedding.")
            return

        self.stdout.write(f"Loading {MODEL_NAME} (downloading ~420MB on first run)...")
        from sentence_transformers import SentenceTransformer
        from huggingface_hub import snapshot_download
        snapshot_download(f"sentence-transformers/{MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        # Flatten all keys across all beats so we encode in one pass
        all_keys = []
        key_counts = []
        for beat in beats:
            all_keys.extend(beat.keys)
            key_counts.append(len(beat.keys))

        self.stdout.write(f"Encoding {len(all_keys)} keys across {count} beats...")
        all_embeddings = model.encode(all_keys, batch_size=256, show_progress_bar=True).tolist()

        # Distribute embeddings back to each beat
        idx = 0
        for beat, n in zip(beats, key_counts):
            beat.key_embeddings = all_embeddings[idx: idx + n]
            idx += n

        Beat.objects.bulk_update(beats, ["key_embeddings"], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"Done. Embedded {count} beats."))

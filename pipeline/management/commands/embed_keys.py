from django.core.management.base import BaseCommand

from pipeline.models import Beat


MODEL_NAME = "all-mpnet-base-v2"


class Command(BaseCommand):
    help = "Compute and store key and premise embeddings for beats that need them"

    def handle(self, *args, **options):
        needs_keys = Beat.objects.exclude(keys=[]).filter(key_embeddings=[])
        needs_premise = Beat.objects.exclude(premise=None).exclude(premise="").filter(premise_embedding=[])

        key_beats = list(needs_keys)
        premise_beats = list(needs_premise)

        if not key_beats and not premise_beats:
            self.stdout.write("No beats need embedding.")
            return

        self.stdout.write(f"Loading {MODEL_NAME} (downloading ~420MB on first run)...")
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer
        snapshot_download(f"sentence-transformers/{MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        if key_beats:
            self.stdout.write(f"Encoding keys for {len(key_beats)} beats...")
            all_keys = []
            key_counts = []
            for beat in key_beats:
                all_keys.extend(beat.keys)
                key_counts.append(len(beat.keys))

            all_key_embeddings = model.encode(all_keys, batch_size=256, show_progress_bar=True).tolist()

            idx = 0
            for beat, n in zip(key_beats, key_counts):
                beat.key_embeddings = all_key_embeddings[idx: idx + n]
                idx += n

            Beat.objects.bulk_update(key_beats, ["key_embeddings"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Keys embedded for {len(key_beats)} beats."))

        if premise_beats:
            self.stdout.write(f"Encoding premises for {len(premise_beats)} beats...")
            premises = [b.premise for b in premise_beats]
            premise_embeddings = model.encode(premises, batch_size=256, show_progress_bar=True).tolist()

            for beat, emb in zip(premise_beats, premise_embeddings):
                beat.premise_embedding = emb

            Beat.objects.bulk_update(premise_beats, ["premise_embedding"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Premises embedded for {len(premise_beats)} beats."))

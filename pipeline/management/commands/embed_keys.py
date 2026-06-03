from django.core.management.base import BaseCommand

from pipeline.models import Beat

MODEL_NAME = "all-mpnet-base-v2"

# The single field whose content most uniquely defines each joke type.
# Formula words are excluded entirely — this is pure content.
DIAGNOSTIC_FIELD = {
    "misdirect":            "reveal",
    "reframe":              "reframe",
    "phonetic-match":       None,   # concatenate heard + reheard below
    "double-meaning":       "comic",
    "contradiction":        None,   # concatenate a + b below
    "analogy":              "shared",
    "hyperbole":            "extreme",
    "elephant-in-the-room": "elephant",
    "anti-humor":           "frame",
}


def _diagnostic_text(beat) -> str | None:
    jt = beat.joke_type or ""
    f = beat.joke_fields or {}
    if jt == "phonetic-match":
        heard = f.get("heard", "")
        reheard = f.get("reheard", "")
        return f"{heard} {reheard}".strip() or None
    if jt == "contradiction":
        a = f.get("a", "")
        b = f.get("b", "")
        return f"{a} {b}".strip() or None
    field = DIAGNOSTIC_FIELD.get(jt)
    if field:
        return f.get(field) or None
    return None


class Command(BaseCommand):
    help = "Compute and store key, premise, and diagnostic embeddings for beats that need them"

    def handle(self, *args, **options):
        all_beats = list(
            Beat.objects.exclude(joke_type=None)
            .exclude(joke_type="")
            .select_related()
        )

        needs_keys = [b for b in all_beats if b.keys and not b.key_embeddings]
        needs_premise = [b for b in all_beats if b.premise and not b.premise_embedding]
        needs_diagnostic = [
            b for b in all_beats
            if _diagnostic_text(b) and not b.diagnostic_embedding
        ]

        if not any([needs_keys, needs_premise, needs_diagnostic]):
            self.stdout.write("No beats need embedding.")
            return

        self.stdout.write(f"Loading {MODEL_NAME} (downloading ~420MB on first run)...")
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer
        snapshot_download(f"sentence-transformers/{MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        if needs_keys:
            self.stdout.write(f"Encoding keys for {len(needs_keys)} beats...")
            all_keys = []
            key_counts = []
            for beat in needs_keys:
                all_keys.extend(beat.keys)
                key_counts.append(len(beat.keys))
            embeddings = model.encode(all_keys, batch_size=256, show_progress_bar=True).tolist()
            idx = 0
            for beat, n in zip(needs_keys, key_counts):
                beat.key_embeddings = embeddings[idx: idx + n]
                idx += n
            Beat.objects.bulk_update(needs_keys, ["key_embeddings"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Keys embedded for {len(needs_keys)} beats."))

        if needs_premise:
            self.stdout.write(f"Encoding premises for {len(needs_premise)} beats...")
            embeddings = model.encode(
                [b.premise for b in needs_premise], batch_size=256, show_progress_bar=True
            ).tolist()
            for beat, emb in zip(needs_premise, embeddings):
                beat.premise_embedding = emb
            Beat.objects.bulk_update(needs_premise, ["premise_embedding"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Premises embedded for {len(needs_premise)} beats."))

        if needs_diagnostic:
            self.stdout.write(f"Encoding diagnostic fields for {len(needs_diagnostic)} beats...")
            texts = [_diagnostic_text(b) for b in needs_diagnostic]
            embeddings = model.encode(texts, batch_size=256, show_progress_bar=True).tolist()
            for beat, emb in zip(needs_diagnostic, embeddings):
                beat.diagnostic_embedding = emb
            Beat.objects.bulk_update(needs_diagnostic, ["diagnostic_embedding"], batch_size=500)
            self.stdout.write(self.style.SUCCESS(f"Diagnostic fields embedded for {len(needs_diagnostic)} beats."))

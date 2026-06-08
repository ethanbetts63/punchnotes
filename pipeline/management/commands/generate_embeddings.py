from django.core.management.base import BaseCommand

from pipeline.models import Beat, Line

MODEL_NAME = "all-mpnet-base-v2"


def _embedding_text(beat) -> str | None:
    lines = (
        Line.objects
        .filter(
            set=beat.bit.set,
            label__in=("setup", "punchline"),
            line_number__gte=beat.line_start,
            line_number__lte=beat.line_end,
        )
        .order_by("line_number")
        .values_list("label", "text")
    )
    setup_parts = []
    punchline_parts = []
    for label, text in lines:
        if label == "setup":
            setup_parts.append(text)
        else:
            punchline_parts.append(text)

    if not punchline_parts:
        return None

    parts = []
    if setup_parts:
        parts.append(" ".join(setup_parts))
    parts.append(" ".join(punchline_parts))
    return " ".join(parts)


class Command(BaseCommand):
    help = "Compute and store embeddings for beats that are missing them"

    def handle(self, *args, **options):
        all_beats = list(
            Beat.objects
            .exclude(joke_type=None)
            .exclude(joke_type="")
            .filter(embedding=[])
            .select_related("bit__set")
        )

        self.stdout.write(f"Checking {len(all_beats)} beats without embeddings...")

        texts = []
        beats_with_text = []
        for beat in all_beats:
            t = _embedding_text(beat)
            if t:
                texts.append(t)
                beats_with_text.append(beat)

        skipped = len(all_beats) - len(beats_with_text)
        if skipped:
            self.stdout.write(f"Skipped {skipped} beats with no punchline lines found.")

        if not beats_with_text:
            self.stdout.write("Nothing to embed.")
            return

        self.stdout.write(f"Loading {MODEL_NAME} (downloading ~420MB on first run)...")
        from huggingface_hub import snapshot_download
        from sentence_transformers import SentenceTransformer
        snapshot_download(f"sentence-transformers/{MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)

        self.stdout.write(f"Encoding setup+punchline text for {len(beats_with_text)} beats...")
        embeddings = model.encode(texts, batch_size=256, show_progress_bar=True).tolist()
        for beat, emb in zip(beats_with_text, embeddings):
            beat.embedding = emb
        Beat.objects.bulk_update(beats_with_text, ["embedding"], batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Embeddings stored for {len(beats_with_text)} beats."
        ))

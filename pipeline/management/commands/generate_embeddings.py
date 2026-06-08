from django.core.management.base import BaseCommand

from pipeline.models import Beat, Line

MODEL_NAME = "all-mpnet-base-v2"
TEXT_FORMAT_CHOICES = ("plain", "structured")


def _load_lines_by_set(beats):
    set_ids = {beat.bit.set_id for beat in beats}
    if not set_ids:
        return {}

    lines_by_set = {}
    lines = (
        Line.objects
        .filter(set_id__in=set_ids, label__in=("setup", "punchline"))
        .order_by("set_id", "line_number")
        .values_list("set_id", "line_number", "label", "text")
    )
    for set_id, line_number, label, text in lines:
        lines_by_set.setdefault(set_id, []).append((line_number, label, text))
    return lines_by_set


def _embedding_text(beat, lines_by_set=None, text_format="plain") -> str | None:
    if lines_by_set is None:
        lines = (
            Line.objects
            .filter(
                set_id=beat.bit.set_id,
                label__in=("setup", "punchline"),
                line_number__gte=beat.line_start,
                line_number__lte=beat.line_end,
            )
            .order_by("line_number")
            .values_list("label", "text")
        )
    else:
        lines = (
            (label, text)
            for line_number, label, text in lines_by_set.get(beat.bit.set_id, [])
            if beat.line_start <= line_number <= beat.line_end
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

    setup_text = " ".join(setup_parts).strip()
    punchline_text = " ".join(punchline_parts).strip()

    if text_format == "structured":
        parts = []
        if setup_text:
            parts.append(f"Setup: {setup_text}")
        parts.append(f"Punchline: {punchline_text}")
        return "\n".join(parts)

    parts = []
    if setup_text:
        parts.append(setup_text)
    parts.append(punchline_text)
    return " ".join(parts)


class Command(BaseCommand):
    help = "Compute and store embeddings for beats that are missing them"

    def add_arguments(self, parser):
        parser.add_argument(
            "--text-format",
            choices=TEXT_FORMAT_CHOICES,
            default="plain",
            help="How to format beat text before embedding (default: plain)",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Regenerate embeddings even for beats that already have one",
        )

    def handle(self, *args, **options):
        text_format = options["text_format"]
        overwrite = options["overwrite"]

        queryset = (
            Beat.objects
            .exclude(joke_type=None)
            .exclude(joke_type="")
            .select_related("bit__set")
            .only(
                "id",
                "bit_id",
                "line_start",
                "line_end",
                "joke_type",
                "embedding",
                "bit__set_id",
            )
        )
        if not overwrite:
            queryset = queryset.filter(embedding=[])
        all_beats = list(queryset)

        if overwrite:
            self.stdout.write(
                f"Checking {len(all_beats)} beats for embedding regeneration using {text_format} text..."
            )
        else:
            self.stdout.write(
                f"Checking {len(all_beats)} beats without embeddings using {text_format} text..."
            )

        lines_by_set = _load_lines_by_set(all_beats)
        texts = []
        beats_with_text = []
        for beat in all_beats:
            t = _embedding_text(beat, lines_by_set=lines_by_set, text_format=text_format)
            if t:
                texts.append(t)
                beats_with_text.append(beat)

        skipped = len(all_beats) - len(beats_with_text)
        if skipped:
            self.stdout.write(f"Skipped {skipped} beats with no punchline lines found.")

        if not beats_with_text:
            self.stdout.write("Nothing to embed.")
            return

        self.stdout.write(f"Loading {MODEL_NAME}...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(MODEL_NAME)

        self.stdout.write(f"Encoding setup+punchline text for {len(beats_with_text)} beats...")
        embeddings = model.encode(texts, batch_size=256, show_progress_bar=True).tolist()
        for beat, emb in zip(beats_with_text, embeddings):
            beat.embedding = emb
        Beat.objects.bulk_update(beats_with_text, ["embedding"], batch_size=500)

        self.stdout.write(self.style.SUCCESS(
            f"Embeddings stored for {len(beats_with_text)} beats."
        ))

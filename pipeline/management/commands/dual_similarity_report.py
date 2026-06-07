# Reads combo_similarity_report.json and scores each matched pair a second time
# using punchline_embedding only. Outputs combined_score = average of both.
# Run combo_similarity_report first, then embed_punchlines if needed.

import json

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat

INPUT_FILENAME = "combo_similarity_report.json"
OUTPUT_FILENAME = "dual_similarity_report.json"


def _fmt(obj, level=0):
    pad = "  " * level
    inner = "  " * (level + 1)
    if isinstance(obj, dict):
        if set(obj.keys()) <= {"label", "text"}:
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{json.dumps(k)}: {_fmt(v, level + 1)}' for k, v in obj.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"
    if isinstance(obj, list):
        if all(isinstance(x, str) for x in obj):
            return json.dumps(obj, ensure_ascii=False)
        items = [f'{inner}{_fmt(v, level + 1)}' for v in obj]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class Command(BaseCommand):
    help = "Score combo-report pairs by punchline similarity and output a dual score"

    def handle(self, *args, **options):
        input_path = settings.PIPELINE_DATA_DIR / INPUT_FILENAME
        if not input_path.exists():
            self.stdout.write(self.style.ERROR(
                f"{INPUT_FILENAME} not found — run combo_similarity_report first."
            ))
            return

        pairs = json.loads(input_path.read_text(encoding="utf-8"))
        self.stdout.write(f"Loaded {len(pairs)} pairs from {INPUT_FILENAME}.")

        beat_ids = {p["beat_a"]["id"] for p in pairs} | {p["beat_b"]["id"] for p in pairs}
        self.stdout.write(f"Fetching punchline embeddings for {len(beat_ids)} beats...")
        punchline_emb = {
            b["id"]: b["punchline_embedding"]
            for b in Beat.objects.filter(id__in=beat_ids).values("id", "punchline_embedding")
        }

        missing = sum(1 for emb in punchline_emb.values() if not emb)
        if missing:
            self.stdout.write(
                f"  Warning: {missing} beats missing punchline embeddings — run embed_punchlines."
            )

        scored = []
        skipped = 0
        for pair in pairs:
            emb_a = punchline_emb.get(pair["beat_a"]["id"])
            emb_b = punchline_emb.get(pair["beat_b"]["id"])
            if not emb_a or not emb_b:
                skipped += 1
                continue
            punchline_sim = round(cosine_sim(emb_a, emb_b), 4)
            combined = round((pair["similarity"] + punchline_sim) / 2, 4)
            scored.append({
                "combined_score": combined,
                "combo_similarity": pair["similarity"],
                "punchline_similarity": punchline_sim,
                "beat_a": pair["beat_a"],
                "beat_b": pair["beat_b"],
            })

        if skipped:
            self.stdout.write(f"Skipped {skipped} pairs with missing punchline embeddings.")

        scored.sort(key=lambda p: p["combined_score"], reverse=True)

        output_path = settings.PIPELINE_DATA_DIR / OUTPUT_FILENAME
        output_path.write_text(_fmt(scored), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"Written {len(scored)} pairs with dual scores to {output_path}"
        ))

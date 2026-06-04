import json
from itertools import combinations

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat, Line

OUTPUT_FILENAME = "combo_similarity_report.json"
DEFAULT_THRESHOLD = 0.70


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


def fetch_lines_for_beats(beat_ids):
    beats = Beat.objects.filter(id__in=beat_ids).select_related("bit__set")
    result = {}
    for beat in beats:
        lines = (
            Line.objects
            .filter(
                set=beat.bit.set,
                label__in=("setup", "punchline", "tag"),
                line_number__gte=beat.line_start,
                line_number__lte=beat.line_end,
            )
            .order_by("line_number")
            .values("label", "text")
        )
        result[beat.id] = list(lines)
    return result


class Command(BaseCommand):
    help = "Report similarity between jokes using joint setup+punchline embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold",
            type=float,
            default=DEFAULT_THRESHOLD,
            help=f"Minimum similarity score to include a pair (default: {DEFAULT_THRESHOLD})",
        )
        parser.add_argument(
            "--joke-type",
            dest="joke_type",
            default=None,
            help="Only compare beats of this joke type",
        )

    def handle(self, *args, **options):
        threshold = options["threshold"]
        joke_type = options["joke_type"]

        qs = (
            Beat.objects
            .exclude(combo_embedding=[])
            .select_related("bit__set__comedian", "bit__set__episode")
        )
        if joke_type:
            qs = qs.filter(joke_type=joke_type)

        beats = list(qs)
        self.stdout.write(f"Loaded {len(beats)} beats with combo embeddings.")

        groups: dict[str, list] = {}
        for beat in beats:
            groups.setdefault(beat.joke_type or "unknown", []).append(beat)

        raw_pairs = []
        for label, group in groups.items():
            n_pairs = len(group) * (len(group) - 1) // 2
            self.stdout.write(f"  {label}: {len(group)} beats, {n_pairs} pairs")
            for a, b in combinations(group, 2):
                if a.bit.set.comedian_id == b.bit.set.comedian_id:
                    continue
                sim = round(cosine_sim(a.combo_embedding, b.combo_embedding), 4)
                if sim >= threshold:
                    raw_pairs.append((sim, a, b))

        raw_pairs.sort(key=lambda p: p[0], reverse=True)

        matched_beat_ids = {a.id for _, a, _ in raw_pairs} | {b.id for _, _, b in raw_pairs}
        self.stdout.write(f"\nFetching lines for {len(matched_beat_ids)} matched beats...")
        lines_by_beat = fetch_lines_for_beats(matched_beat_ids)

        pairs = []
        for sim, a, b in raw_pairs:
            pairs.append({
                "similarity": sim,
                "beat_a": {
                    "id": a.id,
                    "joke_type": a.joke_type,
                    "comedian": a.bit.set.comedian.name,
                    "premise": a.premise,
                    "keys": a.keys,
                    "lines": lines_by_beat.get(a.id, []),
                },
                "beat_b": {
                    "id": b.id,
                    "joke_type": b.joke_type,
                    "comedian": b.bit.set.comedian.name,
                    "premise": b.premise,
                    "keys": b.keys,
                    "lines": lines_by_beat.get(b.id, []),
                },
            })

        output_path = settings.PIPELINE_DATA_DIR / OUTPUT_FILENAME
        output_path.write_text(_fmt(pairs), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"\nFound {len(pairs)} pairs above threshold {threshold}. "
            f"Written to {output_path}"
        ))

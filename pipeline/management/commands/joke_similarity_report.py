# Compares jokes of the same type across different comedians and scores them by
# how semantically similar their premises are, using all-mpnet-base-v2 embeddings.
# Key overlap (key_confidence) is included as a secondary signal but does not
# affect the sort order or threshold — it is there to help a human reviewer judge
# whether a high-scoring premise match is also about the same specific topic.
#
# Known limitations:
#
# 1. Diagnostic field coverage. Not every beat will have a diagnostic_embedding —
#    only beats whose joke_fields were populated at import time (i.e. imported after
#    the joke_fields schema change). Beats imported before that change will be
#    excluded from diagnostic comparison and will fall back to being absent from
#    this report entirely. Re-importing from the archive via reset_db fixes this.
#
# 2. Single-field reductionism. Using one field per joke type (e.g. "reveal" for
#    misdirect, "shared" for analogy) captures the most distinctive content but
#    discards the rest. Two jokes with similar reveals but completely different baits
#    will score high even if they feel like different jokes in context. Key confidence
#    is shown alongside to help a reviewer judge this.
#
# 3. Key confidence is noisy. Keys include abstract mechanism words (e.g.
#    "expertise", "ignorance") that are inherent to the joke-type formula and match
#    across unrelated jokes. A high key_confidence driven by a single generic key
#    is a weak signal; two or more specific content keys matching is meaningful.
#
# 4. Brute-force O(n²) comparison. Fine for the current corpus size. If the corpus
#    grows past ~5,000 beats per type, consider switching to approximate nearest-
#    neighbour search (e.g. FAISS) to keep runtime manageable.
#
# TODO: The algorithm has not been validated against known-similar jokes. Before
#    trusting any scores, seed the database with a handful of manually reworded
#    versions of existing jokes (same mechanism, different wording) and confirm
#    they surface at the top of the report. Until that test passes the scoring
#    approach should be treated as unproven.

import json
from itertools import combinations

import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.models import Beat, Line

OUTPUT_FILENAME = "joke_similarity_report.json"
DEFAULT_THRESHOLD = 0.50


def cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def score_keys(keys_a, embs_a, keys_b, embs_b, threshold=0.78):
    if len(embs_a) <= len(embs_b):
        small_keys, small_embs, big_keys, big_embs = keys_a, embs_a, keys_b, embs_b
    else:
        small_keys, small_embs, big_keys, big_embs = keys_b, embs_b, keys_a, embs_a

    matches = []
    for key, emb in zip(small_keys, small_embs):
        sims = [(cosine_sim(emb, b), bk) for b, bk in zip(big_embs, big_keys)]
        best_sim, best_key = max(sims, key=lambda x: x[0])
        matches.append({"key": key, "matched_key": best_key, "similarity": round(best_sim, 4)})

    above = [m for m in matches if m["similarity"] >= threshold]
    confidence = sum(m["similarity"] for m in above) / len(small_keys) if above else 0.0
    return round(confidence, 4), matches


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
    help = "Report similarity scores between jokes using premise and key embeddings"

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
            help="Only compare beats of this joke type (within-type mode only)",
        )
        parser.add_argument(
            "--cross-type",
            dest="cross_type",
            action="store_true",
            default=False,
            help="Compare all beats regardless of joke type using premise embeddings",
        )

    def handle(self, *args, **options):
        threshold = options["threshold"]
        joke_type = options["joke_type"]
        cross_type = options["cross_type"]

        if cross_type:
            qs = (
                Beat.objects
                .exclude(premise_embedding=[])
                .select_related("bit__set__comedian", "bit__set__episode")
            )
        else:
            qs = (
                Beat.objects
                .exclude(diagnostic_embedding=[])
                .select_related("bit__set__comedian", "bit__set__episode")
            )
            if joke_type:
                qs = qs.filter(joke_type=joke_type)

        beats = list(qs)
        self.stdout.write(f"Loaded {len(beats)} beats with embeddings.")

        if cross_type:
            groups = {"(all types)": beats}
        else:
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

                if cross_type:
                    sim = round(cosine_sim(a.premise_embedding, b.premise_embedding), 4)
                else:
                    sim = round(cosine_sim(a.diagnostic_embedding, b.diagnostic_embedding), 4)

                key_conf, key_matches = score_keys(
                    a.keys, a.key_embeddings,
                    b.keys, b.key_embeddings,
                ) if (a.key_embeddings and b.key_embeddings) else (0.0, [])

                if sim >= threshold:
                    raw_pairs.append((sim, key_conf, key_matches, a, b))

        raw_pairs.sort(key=lambda p: p[0], reverse=True)

        matched_beat_ids = {a.id for _, _, _, a, _ in raw_pairs} | {b.id for _, _, _, _, b in raw_pairs}
        self.stdout.write(f"\nFetching lines for {len(matched_beat_ids)} matched beats...")
        lines_by_beat = fetch_lines_for_beats(matched_beat_ids)

        pairs = []
        for sim, key_conf, key_matches, a, b in raw_pairs:
            pairs.append({
                "similarity": sim,
                "key_confidence": key_conf,
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
                "key_matches": key_matches,
            })

        output_path = settings.PIPELINE_DATA_DIR / OUTPUT_FILENAME
        output_path.write_text(json.dumps(pairs, indent=2), encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(
            f"\nFound {len(pairs)} pairs above threshold {threshold}. "
            f"Written to {output_path}"
        ))

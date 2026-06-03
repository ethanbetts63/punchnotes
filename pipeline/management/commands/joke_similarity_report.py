# Compares jokes of the same type across different comedians and scores them by
# how semantically similar their premises are, using all-mpnet-base-v2 embeddings.
# Key overlap (key_confidence) is included as a secondary signal but does not
# affect the sort order or threshold — it is there to help a human reviewer judge
# whether a high-scoring premise match is also about the same specific topic.
#
# Known limitations:
#
# 1. Premise formula inflation. Every joke type uses a fixed-wording formula
#    (e.g. "is widely understood but rarely said aloud" for elephant-in-the-room,
#    "becomes so extreme that" for hyperbole). Those shared formula words raise the
#    baseline similarity for all pairs within a type, so the useful signal is how
#    far a score sits above that baseline — not the raw number. Elephant-in-the-room
#    and hyperbole are the most affected; reframe and analogy the least.
#
# 2. No genuine duplicates yet. The corpus is original material from Kill Tony
#    comedians. As of the current dataset the max premise similarity across all
#    types is ~0.77. A stolen or heavily derivative joke would likely score 0.85+,
#    which nothing currently does. The report is most useful as a growing-corpus
#    tool: once a match spikes well above the type's usual ceiling it will stand out.
#
# 3. Key confidence is noisy. Keys include abstract mechanism words (e.g.
#    "expertise", "ignorance") that are inherent to the joke-type formula and match
#    across unrelated jokes. A high key_confidence driven by a single generic key
#    is a weak signal; two or more specific keys matching is meaningful.
#
# 4. Brute-force O(n²) comparison. Fine for the current corpus size. If the corpus
#    grows past ~5,000 beats per type, consider switching to approximate nearest-
#    neighbour search (e.g. FAISS) to keep runtime manageable.

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
    help = "Report similarity scores between jokes of the same type using premise and key embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold",
            type=float,
            default=DEFAULT_THRESHOLD,
            help=f"Minimum premise similarity to include a pair (default: {DEFAULT_THRESHOLD})",
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
            .exclude(key_embeddings=[])
            .exclude(premise_embedding=[])
            .select_related("bit__set__comedian", "bit__set__episode")
        )
        if joke_type:
            qs = qs.filter(joke_type=joke_type)

        beats = list(qs)
        self.stdout.write(f"Loaded {len(beats)} beats with embeddings.")

        by_type: dict[str, list] = {}
        for beat in beats:
            by_type.setdefault(beat.joke_type or "unknown", []).append(beat)

        raw_pairs = []
        for jtype, group in by_type.items():
            self.stdout.write(f"  {jtype}: {len(group)} beats, {len(group)*(len(group)-1)//2} pairs")
            for a, b in combinations(group, 2):
                if a.bit.set.comedian_id == b.bit.set.comedian_id:
                    continue

                premise_sim = round(cosine_sim(a.premise_embedding, b.premise_embedding), 4)
                key_conf, key_matches = score_keys(
                    a.keys, a.key_embeddings,
                    b.keys, b.key_embeddings,
                )

                if premise_sim >= threshold:
                    raw_pairs.append((premise_sim, key_conf, key_matches, jtype, a, b))

        raw_pairs.sort(key=lambda p: p[0], reverse=True)

        matched_beat_ids = {a.id for *_, a, _ in raw_pairs} | {b.id for *_, b in raw_pairs}
        self.stdout.write(f"\nFetching lines for {len(matched_beat_ids)} matched beats...")
        lines_by_beat = fetch_lines_for_beats(matched_beat_ids)

        pairs = []
        for premise_sim, key_conf, key_matches, jtype, a, b in raw_pairs:
            pairs.append({
                "premise_similarity": premise_sim,
                "key_confidence": key_conf,
                "joke_type": jtype,
                "beat_a": {
                    "id": a.id,
                    "comedian": a.bit.set.comedian.name,
                    "premise": a.premise,
                    "keys": a.keys,
                    "lines": lines_by_beat.get(a.id, []),
                },
                "beat_b": {
                    "id": b.id,
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

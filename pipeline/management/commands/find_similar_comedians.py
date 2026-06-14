# This command is the discovery half of the comedian-name cleanup flow.
#
# The archive under pipeline/data/bit_annotated_set_archive is treated as raw
# source data and should not be rewritten when a name is misspelled. Instead,
# imports canonicalize names through pipeline/data/comedian_name_relationships.json.
#
# Flow:
#   1. import_sets loads known relationships and applies aliases before DB upsert.
#      This prevents approved spelling variants from creating duplicate comedians.
#   2. At the end of import_sets, this command scans the resulting Comedian rows
#      for fuzzy-similar names and writes unresolved pairs to
#      pipeline/data/similar_comedian_candidates.json.
#   3. An AI/human reviewer uses prompts/comedian_alias_review_prompt.md to mark
#      each pair as alias, not_alias, or uncertain in comedian_name_relationships.json.
#   4. Future imports skip already-decided pairs and apply approved aliases.
#
# Fuzzy matching is intentionally only used for candidate discovery. Runtime
# imports only trust explicit decisions in the relationship file, so a bad
# decision can be undone by editing that JSON and re-importing from the raw archive.

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from pipeline.import_utils.comedian_aliases import (
    decided_pair_keys,
    load_relationships,
    pair_key,
    resolved_alias_slug,
)
from pipeline.models import Comedian


TOKEN_RE = re.compile(r"[a-z0-9]+")
THRESHOLD = 80.0
CANDIDATE_REPORT_FILENAME = "similar_comedian_candidates.json"


@dataclass(frozen=True)
class Candidate:
    score: float
    name_score: float
    token_sort_score: float
    slug_score: float
    first_name: str
    first_slug: str
    second_name: str
    second_slug: str


def normalize_text(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def token_sort_text(value: str) -> str:
    return " ".join(sorted(TOKEN_RE.findall(value.lower())))


def ratio(first: str, second: str) -> float:
    if not first or not second:
        return 0.0
    return SequenceMatcher(None, first, second).ratio() * 100


def pair_score(first: tuple[str, str], second: tuple[str, str]) -> Candidate:
    first_name, first_slug = first
    second_name, second_slug = second

    name_score = ratio(normalize_text(first_name), normalize_text(second_name))
    token_sort_score = ratio(token_sort_text(first_name), token_sort_text(second_name))
    slug_score = ratio(first_slug, second_slug)
    score = max(name_score, token_sort_score, slug_score)

    return Candidate(
        score=score,
        name_score=name_score,
        token_sort_score=token_sort_score,
        slug_score=slug_score,
        first_name=first_name,
        first_slug=first_slug,
        second_name=second_name,
        second_slug=second_slug,
    )


def find_candidates(
    comedians: list[tuple[str, str]],
    threshold: float,
    relationships: dict | None = None,
) -> list[Candidate]:
    relationships = relationships or load_relationships()
    decided_pairs = decided_pair_keys(relationships)
    candidates = []
    for index, first in enumerate(comedians):
        for second in comedians[index + 1:]:
            if pair_key(first[1], second[1]) in decided_pairs:
                continue
            if resolved_alias_slug(first[1], relationships) == resolved_alias_slug(second[1], relationships):
                continue
            candidate = pair_score(first, second)
            if candidate.score >= threshold:
                candidates.append(candidate)
    return sorted(
        candidates,
        key=lambda item: (
            -item.score,
            item.first_slug,
            item.second_slug,
        ),
    )


def candidate_dict(candidate: Candidate) -> dict:
    return {
        "first": {
            "name": candidate.first_name,
            "slug": candidate.first_slug,
        },
        "second": {
            "name": candidate.second_name,
            "slug": candidate.second_slug,
        },
    }


def write_candidate_report(candidates: list[Candidate]) -> str:
    path = settings.PIPELINE_DATA_DIR / CANDIDATE_REPORT_FILENAME
    payload = {
        "threshold": THRESHOLD,
        "candidate_count": len(candidates),
        "candidates": [candidate_dict(candidate) for candidate in candidates],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return str(path)


class Command(BaseCommand):
    help = "Find likely duplicate comedian names using fuzzy matching."

    def handle(self, *args, **options):
        threshold = THRESHOLD
        if threshold < 0 or threshold > 100:
            raise CommandError("THRESHOLD must be between 0 and 100")

        comedians = list(Comedian.objects.order_by("slug").values_list("name", "slug"))
        candidates = find_candidates(comedians, threshold)
        report_path = write_candidate_report(candidates)

        self.stdout.write(f"Comedians scanned: {len(comedians)}")
        self.stdout.write(f"Threshold: {threshold:.1f}")
        self.stdout.write(f"Candidate pairs: {len(candidates)}")
        self.stdout.write(f"Report written: {report_path}")

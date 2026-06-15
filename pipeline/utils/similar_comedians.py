import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from django.conf import settings

from pipeline.utils.comedian_aliases import (
    decided_pair_keys,
    load_relationships,
    pair_key,
    resolved_alias_slug,
)


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


def update_candidate_report(
    new_comedian: tuple[str, str],
    all_comedians: list[tuple[str, str]],
    relationships: dict | None = None,
) -> str:
    relationships = relationships or load_relationships()
    decided_pairs = decided_pair_keys(relationships)

    new_candidates = []
    for other in all_comedians:
        if other[1] == new_comedian[1]:
            continue
        pk = pair_key(new_comedian[1], other[1])
        if pk in decided_pairs:
            continue
        if resolved_alias_slug(new_comedian[1], relationships) == resolved_alias_slug(other[1], relationships):
            continue
        candidate = pair_score(new_comedian, other)
        if candidate.score >= THRESHOLD:
            new_candidates.append(candidate)

    path = settings.PIPELINE_DATA_DIR / CANDIDATE_REPORT_FILENAME
    try:
        existing_list = json.loads(path.read_text(encoding="utf-8")).get("candidates", [])
    except (FileNotFoundError, json.JSONDecodeError):
        existing_list = []

    existing_list = [
        c for c in existing_list
        if pair_key(c["first"]["slug"], c["second"]["slug"]) not in decided_pairs
    ]

    existing_keys = {pair_key(c["first"]["slug"], c["second"]["slug"]) for c in existing_list}
    for candidate in new_candidates:
        pk = pair_key(candidate.first_slug, candidate.second_slug)
        if pk not in existing_keys:
            existing_list.append(candidate_dict(candidate))

    payload = {
        "threshold": THRESHOLD,
        "candidate_count": len(existing_list),
        "candidates": existing_list,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return str(path)

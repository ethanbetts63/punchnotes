import json
import re
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings


RELATIONSHIPS_FILENAME = "comedian_name_relationships.json"
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class CanonicalComedian:
    name: str
    slug: str


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "unknown"


def title_from_slug(slug: str) -> str:
    return " ".join(part.upper() if len(part) <= 2 else part.capitalize() for part in slug.split("-"))


def relationships_path() -> Path:
    return settings.PIPELINE_DATA_DIR / RELATIONSHIPS_FILENAME


def empty_relationships() -> dict:
    return {
        "aliases": {},
        "not_aliases": [],
        "uncertain": [],
    }


def load_relationships(path: Path | None = None) -> dict:
    path = path or relationships_path()
    if not path.exists():
        return empty_relationships()

    data = json.loads(path.read_text(encoding="utf-8"))
    validate_relationships(data)
    return data


def validate_relationships(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("Comedian relationships must be a JSON object.")

    aliases = data.get("aliases", {})
    if not isinstance(aliases, dict):
        raise ValueError("comedian_name_relationships aliases must be an object.")

    for alias_slug, target in aliases.items():
        validate_slug(alias_slug, "alias slug")
        if isinstance(target, str):
            canonical_slug = target
        elif isinstance(target, dict):
            canonical_slug = target.get("canonical_slug")
            canonical_name = target.get("canonical_name")
            if canonical_name is not None and not isinstance(canonical_name, str):
                raise ValueError(f"canonical_name for {alias_slug} must be a string.")
        else:
            raise ValueError(f"Alias target for {alias_slug} must be a slug string or object.")

        validate_slug(canonical_slug, f"canonical slug for {alias_slug}")
        if alias_slug == canonical_slug:
            raise ValueError(f"Alias {alias_slug} cannot point to itself.")

    for section in ("not_aliases", "uncertain"):
        relationships = data.get(section, [])
        if not isinstance(relationships, list):
            raise ValueError(f"comedian_name_relationships {section} must be a list.")
        for index, relationship in enumerate(relationships, start=1):
            first_slug, second_slug = relationship_slugs(relationship)
            validate_slug(first_slug, f"{section} relationship {index} first slug")
            validate_slug(second_slug, f"{section} relationship {index} second slug")
            if first_slug == second_slug:
                raise ValueError(f"{section} relationship {index} cannot compare a slug to itself.")

    validate_alias_graph(aliases)


def validate_slug(value: str, label: str) -> None:
    if not isinstance(value, str) or not SLUG_RE.match(value):
        raise ValueError(f"Invalid {label}: {value!r}")


def alias_target(target: str | dict) -> CanonicalComedian:
    if isinstance(target, str):
        return CanonicalComedian(name=title_from_slug(target), slug=target)
    return CanonicalComedian(
        name=target.get("canonical_name") or title_from_slug(target["canonical_slug"]),
        slug=target["canonical_slug"],
    )


def validate_alias_graph(aliases: dict) -> None:
    for alias_slug in aliases:
        seen = {alias_slug}
        target = alias_target(aliases[alias_slug]).slug
        while target in aliases:
            if target in seen:
                chain = " -> ".join([*seen, target])
                raise ValueError(f"Alias cycle detected: {chain}")
            seen.add(target)
            target = alias_target(aliases[target]).slug


def relationship_slugs(relationship: dict | list | tuple) -> tuple[str, str]:
    if isinstance(relationship, dict):
        if "slugs" in relationship:
            slugs = relationship["slugs"]
            if not isinstance(slugs, list) or len(slugs) != 2:
                raise ValueError("Relationship slugs must contain exactly two slugs.")
            return slugs[0], slugs[1]
        return relationship.get("first_slug"), relationship.get("second_slug")

    if isinstance(relationship, (list, tuple)) and len(relationship) == 2:
        return relationship[0], relationship[1]

    raise ValueError("Relationship must be an object with slugs or a two-item list.")


def pair_key(first_slug: str, second_slug: str) -> tuple[str, str]:
    return tuple(sorted((first_slug, second_slug)))


def resolved_alias(slug: str, relationships: dict | None = None) -> CanonicalComedian:
    relationships = relationships or load_relationships()
    aliases = relationships.get("aliases", {})
    seen = {slug}
    current = slug
    canonical = None

    while current in aliases:
        canonical = alias_target(aliases[current])
        current = canonical.slug
        if current in seen:
            chain = " -> ".join([*seen, current])
            raise ValueError(f"Alias cycle detected: {chain}")
        seen.add(current)

    return canonical or CanonicalComedian(name=title_from_slug(slug), slug=slug)


def resolved_alias_slug(slug: str, relationships: dict | None = None) -> str:
    return resolved_alias(slug, relationships).slug


def canonicalize_comedian_name(name: str, relationships: dict | None = None) -> CanonicalComedian:
    relationships = relationships or load_relationships()
    raw_slug = slugify(name)
    canonical = resolved_alias(raw_slug, relationships)
    if canonical.slug == raw_slug:
        return CanonicalComedian(name=name, slug=raw_slug)

    return CanonicalComedian(name=canonical.name, slug=canonical.slug)


def decided_pair_keys(relationships: dict | None = None) -> set[tuple[str, str]]:
    relationships = relationships or load_relationships()
    keys = set()

    for alias_slug, target in relationships.get("aliases", {}).items():
        keys.add(pair_key(alias_slug, alias_target(target).slug))
        keys.add(pair_key(alias_slug, resolved_alias_slug(alias_slug, relationships)))

    for section in ("not_aliases", "uncertain"):
        for relationship in relationships.get(section, []):
            keys.add(pair_key(*relationship_slugs(relationship)))

    return keys

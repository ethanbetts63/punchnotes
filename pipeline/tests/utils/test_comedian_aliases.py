import pytest

from pipeline.utils.comedian_aliases import (
    canonicalize_comedian_name,
    decided_pair_keys,
    empty_relationships,
    pair_key,
    validate_relationships,
)


def test_canonicalizes_alias_to_configured_name_and_slug():
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}

    result = canonicalize_comedian_name("Ari Mati", relationships)

    assert result.name == "Ari Matti"
    assert result.slug == "ari-matti"


def test_preserves_unknown_names():
    result = canonicalize_comedian_name("New Comic", empty_relationships())

    assert result.name == "New Comic"
    assert result.slug == "new-comic"


def test_follows_alias_chain():
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matty"}
    relationships["aliases"]["ari-matty"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}

    result = canonicalize_comedian_name("Ari Mati", relationships)

    assert result.name == "Ari Matti"
    assert result.slug == "ari-matti"


def test_decided_pair_keys_covers_all_relationship_types():
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}
    relationships["aliases"]["ari-matty"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}
    relationships["not_aliases"].append({"slugs": ["rob-white", "ron-white"]})
    relationships["uncertain"].append({"slugs": ["jim-talley", "jim-telly"]})

    keys = decided_pair_keys(relationships)

    assert pair_key("ari-mati", "ari-matti") in keys
    assert pair_key("ari-matty", "ari-matti") in keys
    assert pair_key("rob-white", "ron-white") in keys
    assert pair_key("jim-talley", "jim-telly") in keys


def test_validate_relationships_rejects_alias_cycle():
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti"}
    relationships["aliases"]["ari-matti"] = {"canonical_slug": "ari-mati"}

    with pytest.raises(ValueError):
        validate_relationships(relationships)

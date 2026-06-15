from pipeline.utils.similar_comedians import find_candidates
from pipeline.utils.comedian_aliases import empty_relationships


def test_finds_close_name_variants():
    comedians = [("Ari Mati", "ari-mati"), ("Ari Matti", "ari-matti"), ("William Montgomery", "william-montgomery")]
    candidates = find_candidates(comedians, threshold=85, relationships=empty_relationships())

    assert len(candidates) == 1
    assert candidates[0].first_slug == "ari-mati"
    assert candidates[0].second_slug == "ari-matti"


def test_threshold_filters_weaker_matches():
    comedians = [("Rick Diaz", "rick-diaz"), ("Ric Diez", "ric-diez")]

    assert find_candidates(comedians, threshold=95, relationships=empty_relationships()) == []
    assert len(find_candidates(comedians, threshold=80, relationships=empty_relationships())) == 1


def test_skips_decided_relationships():
    comedians = [("Ari Mati", "ari-mati"), ("Ari Matti", "ari-matti")]
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}

    assert find_candidates(comedians, threshold=85, relationships=relationships) == []


def test_skips_pairs_with_same_resolved_canonical_slug():
    comedians = [("Ari Mati", "ari-mati"), ("Ari Matty", "ari-matty")]
    relationships = empty_relationships()
    relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}
    relationships["aliases"]["ari-matty"] = {"canonical_slug": "ari-matti", "canonical_name": "Ari Matti"}

    assert find_candidates(comedians, threshold=80, relationships=relationships) == []

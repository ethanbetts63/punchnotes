import pytest

from api.set_slugs import filter_sets_by_public_slugs, lookup_set_by_public_slug, set_public_slug
from pipeline.models import Comedian, Set, Video


pytestmark = pytest.mark.django_db


def _make_set(video_id, start_seconds, slug, video_number=700):
    video, _ = Video.objects.get_or_create(
        video_id=video_id,
        defaults={"number": video_number, "title": f"KT #{video_number}", "url": f"https://example.com/{video_number}"},
    )
    comedian = Comedian.objects.create(name=slug.title(), slug=slug)
    return Set.objects.create(video=video, comedian=comedian, start_seconds=start_seconds)


def test_set_public_slug_has_no_ordinal():
    s = _make_set("aaa0000001", 142.0, "casey-rocket")
    assert set_public_slug(s) == "aaa0000001-142-casey-rocket"


def test_lookup_set_by_public_slug_finds_exact_match():
    s = _make_set("aaa0000001", 142.0, "casey-rocket")
    found = lookup_set_by_public_slug("aaa0000001-142-casey-rocket")
    assert list(found) == [s]


def test_lookup_set_by_public_slug_matches_truncated_start_seconds():
    s = _make_set("aaa0000001", 142.7, "casey-rocket")
    found = lookup_set_by_public_slug("aaa0000001-142-casey-rocket")
    assert list(found) == [s]


def test_lookup_set_by_public_slug_returns_none_for_garbage():
    assert list(lookup_set_by_public_slug("not-a-slug!!")) == []


def test_lookup_set_by_public_slug_unaffected_by_resequencing():
    """The whole point of dropping the ordinal: a second set appearing
    earlier in the episode must not change this set's slug."""
    s = _make_set("aaa0000001", 300.0, "late-comic")
    slug_before = set_public_slug(s)
    _make_set("aaa0000001", 100.0, "early-comic", video_number=700)

    s.refresh_from_db()
    assert set_public_slug(s) == slug_before
    assert list(lookup_set_by_public_slug(slug_before)) == [s]


def test_filter_sets_by_public_slugs_matches_multiple():
    s1 = _make_set("aaa0000001", 100.0, "casey-rocket")
    s2 = _make_set("aaa0000002", 200.0, "dana-blue", video_number=701)
    result = filter_sets_by_public_slugs(
        Set.objects.all(),
        ["aaa0000001-100-casey-rocket", "aaa0000002-200-dana-blue"],
    )
    assert set(result) == {s1, s2}


def test_lookup_set_by_legacy_ordinal_slug_finds_the_set():
    _make_set("aaa0000001", 100.0, "early-comic")
    s = _make_set("aaa0000001", 300.0, "pat-o-neill")
    assert list(lookup_set_by_public_slug("aaa0000001-set02-pat-o-neill")) == [s]


def test_lookup_set_by_legacy_slug_uses_the_ordinal_when_a_comic_appears_twice():
    _make_set("aaa0000001", 100.0, "pat-o-neill")
    second = Set.objects.create(
        video=Video.objects.get(video_id="aaa0000001"),
        comedian=Comedian.objects.get(slug="pat-o-neill"),
        start_seconds=300.0,
    )
    assert list(lookup_set_by_public_slug("aaa0000001-set02-pat-o-neill")) == [second]


def test_lookup_set_by_legacy_slug_returns_none_for_an_unknown_comic():
    _make_set("aaa0000001", 100.0, "casey-rocket")
    assert list(lookup_set_by_public_slug("aaa0000001-set01-someone-else")) == []

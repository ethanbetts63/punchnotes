import pytest
from django.core.exceptions import ValidationError

from pipeline.models import Comedian, Line, Set, Video
from pipeline.models.comedian import validate_attributes
from pipeline.utils.update.records import (
    _bit_ratios,
    merge_attributes,
    refresh_set_ratios,
    upsert_comedian,
    upsert_set,
)


pytestmark = pytest.mark.django_db


# --- merge_attributes ---

def test_merge_attributes_deduplicates_preserving_order():
    assert merge_attributes(["gay", "black"], ["black", "woman"]) == ["gay", "black", "woman"]

def test_merge_attributes_empty_existing():
    assert merge_attributes([], ["gay"]) == ["gay"]

def test_merge_attributes_empty_incoming():
    assert merge_attributes(["gay"], []) == ["gay"]

def test_merge_attributes_both_empty():
    assert merge_attributes([], []) == []

def test_merge_attributes_none_raises():
    with pytest.raises(TypeError):
        merge_attributes(None, None)

def test_merge_attributes_filters_falsy():
    assert merge_attributes(["gay", ""], ["", "black"]) == ["gay", "black"]


# --- upsert_comedian attributes ---

_base_meta = {"comedian_name": "Test Comic"}

def test_creates_comedian_with_attributes():
    comedian = upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["gay", "black"]})
    assert comedian.attributes == ["gay", "black"]

def test_merges_new_attributes_on_reimport():
    upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["gay"]})
    comedian = upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["black"]})
    assert comedian.attributes == ["gay", "black"]

def test_no_duplicate_attributes_on_reimport():
    upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["gay"]})
    comedian = upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["gay"]})
    assert comedian.attributes == ["gay"]

def test_missing_attributes_key_is_tolerated():
    comedian = upsert_comedian("test-comic", _base_meta)
    assert comedian.attributes == []

def test_known_regular_overrides_incoming_appearance_attribute():
    meta = {**_base_meta, "comedian_name": "William Montgomery", "comedian_attributes": ["bucket_pull", "man"]}
    comedian = upsert_comedian("william-montgomery", meta)
    assert comedian.attributes == ["regular", "man"]

def test_known_golden_ticket_overrides_incoming_appearance_attribute():
    meta = {**_base_meta, "comedian_name": "Jack Shaw", "comedian_attributes": ["regular", "man"]}
    comedian = upsert_comedian("jack-shaw", meta)
    assert comedian.attributes == ["golden_ticket", "man"]

def test_known_special_overrides_incoming_appearance_attribute():
    meta = {**_base_meta, "comedian_name": "Ron White", "comedian_attributes": ["regular", "man"]}
    comedian = upsert_comedian("ron-white", meta)
    assert comedian.attributes == ["special", "man"]

def test_unknown_regular_normalizes_to_bucket_pull():
    comedian = upsert_comedian("test-comic", {**_base_meta, "comedian_attributes": ["regular", "woman"]})
    assert comedian.attributes == ["bucket_pull", "woman"]


# --- upsert_set ordering ---

def _set_meta(name, start_seconds):
    return {
        "comedian_name": name,
        "start_seconds": start_seconds,
        "interview_end_line": None,
        "interview_end_seconds": None,
        "set_attributes": [],
    }

def test_sets_ordered_by_start_seconds():
    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    late = upsert_comedian("late-comic", _set_meta("Late Comic", 300))
    early = upsert_comedian("early-comic", _set_meta("Early Comic", 100))
    upsert_set(episode, late, _set_meta("Late Comic", 300))
    upsert_set(episode, early, _set_meta("Early Comic", 100))

    ordered = list(Set.objects.filter(video=episode).order_by("start_seconds"))
    assert [s.comedian.name for s in ordered] == ["Early Comic", "Late Comic"]

def test_reimport_same_start_updates_existing_set():
    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    comic = upsert_comedian("test-comic", _set_meta("Test Comic", 100))
    first = upsert_set(episode, comic, _set_meta("Test Comic", 100))
    second = upsert_set(episode, comic, {**_set_meta("Test Comic", 100), "set_attributes": ["large_joke_book"]})

    assert first.id == second.id
    assert Set.objects.filter(video=episode).count() == 1
    assert second.attributes == ["large_joke_book"]

# --- _bit_ratios ---

def test_tag_density_is_tags_per_punchline():
    lines = [
        {"line_number": 1, "label": "setup"},
        {"line_number": 2, "label": "punchline"},
        {"line_number": 3, "label": "tag"},
        {"line_number": 4, "label": "punchline"},
    ]
    label_by_line = {l["line_number"]: l["label"] for l in lines}
    punch_density, tag_density = _bit_ratios(label_by_line, {1, 2, 3, 4})

    assert punch_density == 3.0
    assert tag_density == 0.5

def test_refresh_set_ratios_stores_values():
    comedian = Comedian.objects.create(name="Test Comic", slug="test-comic")
    video = Video.objects.create(video_id="abc123xyz01", title="KT #1", url="https://example.com")
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=0)
    Line.objects.bulk_create([
        Line(set=set_obj, line_number=1, label="setup", text="Setup", start_seconds=0),
        Line(set=set_obj, line_number=2, label="punchline", text="Punch one", start_seconds=1),
        Line(set=set_obj, line_number=3, label="tag", text="Tag one", start_seconds=2),
        Line(set=set_obj, line_number=4, label="punchline", text="Punch two", start_seconds=3),
    ])

    refresh_set_ratios(set_obj)
    set_obj.refresh_from_db()

    assert set_obj.punch_density == 3.0
    assert set_obj.tag_density == 0.5


# --- validate_attributes ---

def test_accepts_allowed_attributes():
    validate_attributes(["gay", "middle-age", "young"])

def test_rejects_unknown_attribute():
    with pytest.raises(ValidationError):
        validate_attributes(["funny"])

def test_rejects_non_list_value():
    with pytest.raises(ValidationError):
        validate_attributes("gay")

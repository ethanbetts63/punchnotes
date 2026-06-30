import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

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

def test_set_numbers_derived_from_start_seconds():
    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    late = upsert_comedian("late-comic", _set_meta("Late Comic", 300))
    early = upsert_comedian("early-comic", _set_meta("Early Comic", 100))
    upsert_set(episode, late, _set_meta("Late Comic", 300))
    upsert_set(episode, early, _set_meta("Early Comic", 100))

    ordered = list(Set.objects.filter(video=episode).order_by("start_seconds"))
    assert [s.comedian.name for s in ordered] == ["Early Comic", "Late Comic"]
    assert [s.set_number for s in ordered] == [1, 2]

def test_reimport_same_start_updates_existing_set():
    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    comic = upsert_comedian("test-comic", _set_meta("Test Comic", 100))
    first = upsert_set(episode, comic, _set_meta("Test Comic", 100))
    second = upsert_set(episode, comic, {**_set_meta("Test Comic", 100), "set_attributes": ["large_joke_book"]})

    assert first.id == second.id
    assert Set.objects.filter(video=episode).count() == 1
    assert second.attributes == ["large_joke_book"]

def test_resequence_handles_existing_high_set_numbers():
    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    first_comic = upsert_comedian("first-comic", _set_meta("First Comic", 100))
    second_comic = upsert_comedian("second-comic", _set_meta("Second Comic", 200))
    first = upsert_set(episode, first_comic, _set_meta("First Comic", 100))
    second = upsert_set(episode, second_comic, _set_meta("Second Comic", 200))
    first.set_number = 3
    first.save(update_fields=["set_number"])
    second.set_number = 4
    second.save(update_fields=["set_number"])

    upsert_set(episode, second_comic, _set_meta("Second Comic", 200))

    ordered = list(Set.objects.filter(video=episode).order_by("start_seconds"))
    assert [s.set_number for s in ordered] == [1, 2]


# --- resequence image renaming ---

def test_resequence_renames_image_files_and_updates_image_url(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    early_comic = upsert_comedian("early-comic", _set_meta("Early Comic", 100))
    late_comic = upsert_comedian("late-comic", _set_meta("Late Comic", 200))

    late = upsert_set(episode, late_comic, _set_meta("Late Comic", 200))
    late.image_url = "set-images/KT1_set01_late-comic.jpg"
    late.save(update_fields=["image_url"])
    (public_dir / "KT1_set01_late-comic.jpg").write_bytes(b"img")
    (archive_dir / "KT1_set01_late-comic.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        upsert_set(episode, early_comic, _set_meta("Early Comic", 100))

    late.refresh_from_db()
    assert late.set_number == 2
    assert late.image_url == "set-images/KT1_set02_late-comic.jpg"
    assert (public_dir / "KT1_set02_late-comic.jpg").exists()
    assert not (public_dir / "KT1_set01_late-comic.jpg").exists()
    assert (archive_dir / "KT1_set02_late-comic.jpg").exists()
    assert not (archive_dir / "KT1_set01_late-comic.jpg").exists()


def test_resequence_skips_rename_when_no_image(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    early_comic = upsert_comedian("early-comic", _set_meta("Early Comic", 100))
    late_comic = upsert_comedian("late-comic", _set_meta("Late Comic", 200))
    upsert_set(episode, late_comic, _set_meta("Late Comic", 200))

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        upsert_set(episode, early_comic, _set_meta("Early Comic", 100))

    late = Set.objects.get(video=episode, comedian=late_comic)
    assert late.set_number == 2
    assert late.image_url is None


def test_resequence_renames_only_public_file_when_not_in_archive(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    episode = Video.objects.create(video_id="test123", number=1, title="KT #1 - Test Guest", url="https://www.youtube.com/watch?v=test123")
    early_comic = upsert_comedian("early-comic", _set_meta("Early Comic", 100))
    late_comic = upsert_comedian("late-comic", _set_meta("Late Comic", 200))

    late = upsert_set(episode, late_comic, _set_meta("Late Comic", 200))
    late.image_url = "set-images/KT1_set01_late-comic.jpg"
    late.save(update_fields=["image_url"])
    (public_dir / "KT1_set01_late-comic.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        upsert_set(episode, early_comic, _set_meta("Early Comic", 100))

    late.refresh_from_db()
    assert late.image_url == "set-images/KT1_set02_late-comic.jpg"
    assert (public_dir / "KT1_set02_late-comic.jpg").exists()
    assert not (archive_dir / "KT1_set01_late-comic.jpg").exists()


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
    set_obj = Set.objects.create(video=video, comedian=comedian, set_number=1, start_seconds=0)
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

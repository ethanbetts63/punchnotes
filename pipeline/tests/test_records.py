from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase

from pipeline.import_utils.records import merge_attributes, upsert_comedian, upsert_episode, upsert_set
from pipeline.models import Set
from pipeline.models.comedian import validate_attributes


class MergeAttributesTests(TestCase):
    def test_deduplicates_preserving_order(self):
        result = merge_attributes(["gay", "black"], ["black", "woman"])
        self.assertEqual(result, ["gay", "black", "woman"])

    def test_empty_existing(self):
        result = merge_attributes([], ["gay"])
        self.assertEqual(result, ["gay"])

    def test_empty_incoming(self):
        result = merge_attributes(["gay"], [])
        self.assertEqual(result, ["gay"])

    def test_both_empty(self):
        result = merge_attributes([], [])
        self.assertEqual(result, [])

    def test_none_treated_as_empty(self):
        result = merge_attributes(None, None)
        self.assertEqual(result, [])

    def test_filters_falsy_values(self):
        result = merge_attributes(["gay", ""], ["", "black"])
        self.assertEqual(result, ["gay", "black"])


class UpsertComedianAttributesTests(TestCase):
    _base_meta = {
        "comedian_name": "Test Comic",
        "comedian_type": "regular",
    }

    def test_creates_comedian_with_attributes(self):
        meta = {**self._base_meta, "attributes": ["gay", "black"]}
        comedian = upsert_comedian("test-comic", meta)
        self.assertEqual(comedian.attributes, ["gay", "black"])

    def test_merges_new_attributes_on_reimport(self):
        upsert_comedian("test-comic", {**self._base_meta, "attributes": ["gay"]})
        comedian = upsert_comedian("test-comic", {**self._base_meta, "attributes": ["black"]})
        self.assertEqual(comedian.attributes, ["gay", "black"])

    def test_no_duplicate_attributes_on_reimport(self):
        upsert_comedian("test-comic", {**self._base_meta, "attributes": ["gay"]})
        comedian = upsert_comedian("test-comic", {**self._base_meta, "attributes": ["gay"]})
        self.assertEqual(comedian.attributes, ["gay"])

    def test_missing_attributes_key_is_tolerated(self):
        comedian = upsert_comedian("test-comic", self._base_meta)
        self.assertEqual(comedian.attributes, [])


class UpsertSetOrderingTests(TestCase):
    _episode_meta = {
        "episode_title": "KT #1 - Test Guest",
        "episode_url": "https://www.youtube.com/watch?v=test123",
        "publish_date": None,
    }

    def _set_meta(self, name, start_seconds):
        return {
            **self._episode_meta,
            "comedian_name": name,
            "comedian_type": "bucket_pull",
            "start_seconds": start_seconds,
            "interview_end_line": None,
            "interview_end_seconds": None,
            "joke_book": None,
        }

    def test_set_numbers_are_derived_from_start_seconds(self):
        episode = upsert_episode("test123", self._episode_meta)
        late = upsert_comedian("late-comic", self._set_meta("Late Comic", 300))
        early = upsert_comedian("early-comic", self._set_meta("Early Comic", 100))

        upsert_set(episode, late, self._set_meta("Late Comic", 300))
        upsert_set(episode, early, self._set_meta("Early Comic", 100))

        ordered = list(Set.objects.filter(episode=episode).order_by("start_seconds"))
        self.assertEqual([s.comedian.name for s in ordered], ["Early Comic", "Late Comic"])
        self.assertEqual([s.set_number for s in ordered], [1, 2])

    def test_reimport_same_start_updates_existing_set(self):
        episode = upsert_episode("test123", self._episode_meta)
        comic = upsert_comedian("test-comic", self._set_meta("Test Comic", 100))

        first = upsert_set(episode, comic, self._set_meta("Test Comic", 100))
        second = upsert_set(episode, comic, {**self._set_meta("Test Comic", 100), "joke_book": "large"})

        self.assertEqual(first.id, second.id)
        self.assertEqual(Set.objects.filter(episode=episode).count(), 1)
        self.assertEqual(second.set_number, 1)
        self.assertEqual(second.joke_book, "large")

    def test_reimport_same_start_can_update_comedian(self):
        episode = upsert_episode("test123", self._episode_meta)
        first_comic = upsert_comedian("first-comic", self._set_meta("First Comic", 100))
        corrected_comic = upsert_comedian("corrected-comic", self._set_meta("Corrected Comic", 100))

        first = upsert_set(episode, first_comic, self._set_meta("First Comic", 100))
        second = upsert_set(episode, corrected_comic, self._set_meta("Corrected Comic", 100))

        self.assertEqual(first.id, second.id)
        self.assertEqual(Set.objects.filter(episode=episode).count(), 1)
        self.assertEqual(second.comedian.name, "Corrected Comic")

    def test_resequence_handles_existing_high_set_numbers(self):
        episode = upsert_episode("test123", self._episode_meta)
        first_comic = upsert_comedian("first-comic", self._set_meta("First Comic", 100))
        second_comic = upsert_comedian("second-comic", self._set_meta("Second Comic", 200))

        first = upsert_set(episode, first_comic, self._set_meta("First Comic", 100))
        second = upsert_set(episode, second_comic, self._set_meta("Second Comic", 200))
        first.set_number = 3
        first.save(update_fields=["set_number"])
        second.set_number = 4
        second.save(update_fields=["set_number"])

        upsert_set(episode, second_comic, self._set_meta("Second Comic", 200))

        ordered = list(Set.objects.filter(episode=episode).order_by("start_seconds"))
        self.assertEqual([s.set_number for s in ordered], [1, 2])


class ValidateComedianAttributesTests(SimpleTestCase):
    def test_accepts_allowed_attributes_and_nationality(self):
        validate_attributes(["gay", "middle-age", "young", "nationality:canada"])

    def test_rejects_unknown_attribute(self):
        with self.assertRaises(ValidationError):
            validate_attributes(["funny"])

    def test_rejects_non_list_value(self):
        with self.assertRaises(ValidationError):
            validate_attributes("gay")

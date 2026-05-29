from django.test import TestCase

from pipeline.import_utils.records import merge_attributes, upsert_comedian


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
        meta = {**self._base_meta, "comedian_attributes": ["gay", "black"]}
        comedian = upsert_comedian("test-comic", meta)
        self.assertEqual(comedian.comedian_attributes, ["gay", "black"])

    def test_merges_new_attributes_on_reimport(self):
        upsert_comedian("test-comic", {**self._base_meta, "comedian_attributes": ["gay"]})
        comedian = upsert_comedian("test-comic", {**self._base_meta, "comedian_attributes": ["black"]})
        self.assertEqual(comedian.comedian_attributes, ["gay", "black"])

    def test_no_duplicate_attributes_on_reimport(self):
        upsert_comedian("test-comic", {**self._base_meta, "comedian_attributes": ["gay"]})
        comedian = upsert_comedian("test-comic", {**self._base_meta, "comedian_attributes": ["gay"]})
        self.assertEqual(comedian.comedian_attributes, ["gay"])

    def test_missing_attributes_key_is_tolerated(self):
        comedian = upsert_comedian("test-comic", self._base_meta)
        self.assertEqual(comedian.comedian_attributes, [])

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from pipeline.management.commands.extract_set import normalize_attributes


class ExtractSetTests(SimpleTestCase):
    def test_normalizes_attributes(self):
        self.assertEqual(
            normalize_attributes("Gay, black, middle eastern, middle-age, old, young, nationality:Canada"),
            ["gay", "black", "middle_eastern", "middle-age", "old", "young", "nationality:canada"],
        )

    def test_attributes_are_deduplicated(self):
        self.assertEqual(
            normalize_attributes("gay, gay, GAY"),
            ["gay"],
        )

    def test_rejects_unknown_comedian_attribute(self):
        with self.assertRaises(CommandError):
            normalize_attributes("funny")

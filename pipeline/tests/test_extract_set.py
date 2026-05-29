from django.core.management.base import CommandError
from django.test import SimpleTestCase

from pipeline.management.commands.extract_set import normalize_comedian_attributes


class ExtractSetTests(SimpleTestCase):
    def test_normalizes_comedian_attributes(self):
        self.assertEqual(
            normalize_comedian_attributes("Gay, black, middle eastern, nationality:Canada"),
            ["gay", "black", "middle_eastern", "nationality:canada"],
        )

    def test_comedian_attributes_are_deduplicated(self):
        self.assertEqual(
            normalize_comedian_attributes("gay, gay, GAY"),
            ["gay"],
        )

    def test_rejects_unknown_comedian_attribute(self):
        with self.assertRaises(CommandError):
            normalize_comedian_attributes("funny")

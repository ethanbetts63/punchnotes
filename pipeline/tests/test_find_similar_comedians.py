from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from pipeline.management.commands.find_similar_comedians import find_candidates
from pipeline.models import Comedian


class FindSimilarComediansTests(TestCase):
    def test_finds_close_name_variants(self):
        comedians = [
            ("Ari Mati", "ari-mati"),
            ("Ari Matti", "ari-matti"),
            ("William Montgomery", "william-montgomery"),
        ]

        candidates = find_candidates(comedians, threshold=85)

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].first_slug, "ari-mati")
        self.assertEqual(candidates[0].second_slug, "ari-matti")

    def test_threshold_filters_weaker_matches(self):
        comedians = [
            ("Rick Diaz", "rick-diaz"),
            ("Ric Diez", "ric-diez"),
        ]

        self.assertEqual(find_candidates(comedians, threshold=95), [])
        self.assertEqual(len(find_candidates(comedians, threshold=80)), 1)

    def test_command_prints_candidate_pairs(self):
        Comedian.objects.create(name="Dedric Flynn", slug="dedric-flynn")
        Comedian.objects.create(name="Dedrick Flynn", slug="dedrick-flynn")
        Comedian.objects.create(name="Jack Shaw", slug="jack-shaw")

        output = StringIO()
        call_command(
            "find_similar_comedians",
            threshold=85,
            stdout=output,
        )

        text = output.getvalue()
        self.assertIn("Dedric Flynn [dedric-flynn]", text)
        self.assertIn("Dedrick Flynn [dedrick-flynn]", text)
        self.assertNotIn("Jack Shaw", text)

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import override_settings
from django.test import TestCase

from pipeline.management.commands.find_similar_comedians import find_candidates
from pipeline.import_utils.comedian_aliases import empty_relationships
from pipeline.models import Comedian


class FindSimilarComediansTests(TestCase):
    def test_finds_close_name_variants(self):
        comedians = [
            ("Ari Mati", "ari-mati"),
            ("Ari Matti", "ari-matti"),
            ("William Montgomery", "william-montgomery"),
        ]

        candidates = find_candidates(comedians, threshold=85, relationships=empty_relationships())

        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].first_slug, "ari-mati")
        self.assertEqual(candidates[0].second_slug, "ari-matti")

    def test_threshold_filters_weaker_matches(self):
        comedians = [
            ("Rick Diaz", "rick-diaz"),
            ("Ric Diez", "ric-diez"),
        ]

        self.assertEqual(find_candidates(comedians, threshold=95, relationships=empty_relationships()), [])
        self.assertEqual(len(find_candidates(comedians, threshold=80, relationships=empty_relationships())), 1)

    def test_skips_defined_relationships(self):
        comedians = [
            ("Ari Mati", "ari-mati"),
            ("Ari Matti", "ari-matti"),
        ]
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }

        self.assertEqual(find_candidates(comedians, threshold=85, relationships=relationships), [])

    def test_skips_pairs_with_same_resolved_canonical_slug(self):
        comedians = [
            ("Ari Mati", "ari-mati"),
            ("Ari Matty", "ari-matty"),
        ]
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }
        relationships["aliases"]["ari-matty"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }

        self.assertEqual(find_candidates(comedians, threshold=80, relationships=relationships), [])

    def test_command_prints_candidate_pairs(self):
        Comedian.objects.create(name="Dedric Flynn", slug="dedric-flynn")
        Comedian.objects.create(name="Dedrick Flynn", slug="dedrick-flynn")
        Comedian.objects.create(name="Jack Shaw", slug="jack-shaw")

        with TemporaryDirectory() as tmp:
            with override_settings(PIPELINE_DATA_DIR=Path(tmp)):
                output = StringIO()
                call_command(
                    "find_similar_comedians",
                    stdout=output,
                )

                report_path = Path(tmp) / "similar_comedian_candidates.json"
                text = output.getvalue()
                self.assertIn("Dedric Flynn [dedric-flynn]", text)
                self.assertIn("Dedrick Flynn [dedrick-flynn]", text)
                self.assertNotIn("Jack Shaw", text)
                self.assertTrue(report_path.exists())

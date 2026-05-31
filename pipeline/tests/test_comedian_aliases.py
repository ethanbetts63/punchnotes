from django.test import SimpleTestCase

from pipeline.import_utils.comedian_aliases import (
    canonicalize_comedian_name,
    decided_pair_keys,
    empty_relationships,
    pair_key,
    validate_relationships,
)


class ComedianAliasesTests(SimpleTestCase):
    def test_canonicalizes_alias_to_configured_name_and_slug(self):
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
            "notes": "Supported spelling.",
        }

        canonical = canonicalize_comedian_name("Ari Mati", relationships)

        self.assertEqual(canonical.name, "Ari Matti")
        self.assertEqual(canonical.slug, "ari-matti")

    def test_preserves_unknown_names(self):
        canonical = canonicalize_comedian_name("New Comic", empty_relationships())

        self.assertEqual(canonical.name, "New Comic")
        self.assertEqual(canonical.slug, "new-comic")

    def test_follows_alias_chain_to_final_canonical_name(self):
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matty"}
        relationships["aliases"]["ari-matty"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }

        canonical = canonicalize_comedian_name("Ari Mati", relationships)

        self.assertEqual(canonical.name, "Ari Matti")
        self.assertEqual(canonical.slug, "ari-matti")

    def test_decided_pair_keys_include_all_relationship_types(self):
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }
        relationships["aliases"]["ari-matty"] = {
            "canonical_slug": "ari-matti",
            "canonical_name": "Ari Matti",
        }
        relationships["not_aliases"].append({"slugs": ["rob-white", "ron-white"]})
        relationships["uncertain"].append({"slugs": ["jim-talley", "jim-telly"]})

        keys = decided_pair_keys(relationships)

        self.assertIn(pair_key("ari-mati", "ari-matti"), keys)
        self.assertIn(pair_key("ari-matty", "ari-matti"), keys)
        self.assertIn(pair_key("rob-white", "ron-white"), keys)
        self.assertIn(pair_key("jim-talley", "jim-telly"), keys)

    def test_rejects_alias_cycle(self):
        relationships = empty_relationships()
        relationships["aliases"]["ari-mati"] = {"canonical_slug": "ari-matti"}
        relationships["aliases"]["ari-matti"] = {"canonical_slug": "ari-mati"}

        with self.assertRaises(ValueError):
            validate_relationships(relationships)

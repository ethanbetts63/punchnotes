from django.test import SimpleTestCase

from pipeline.import_utils.cleaning import clean_fluff_bit_beat
from pipeline.import_utils.validation import validate_bit_meta


def valid_meta_with_line(line):
    return {
        "bit_meta": {
            "1": {
                "beats": {
                    "1": {
                        "premise": "A thing could be an unexpected thing.",
                        "joke_type": "reframe",
                        "topics": ["thing"],
                    }
                }
            }
        },
        "lines": [line],
    }


class CleanFluffBitBeatTests(SimpleTestCase):
    def test_setup_gets_next_punchline_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
                {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertEqual(cleaned["lines"][0]["bit"], 1)
        self.assertEqual(cleaned["lines"][0]["beat"], 1)

    def test_tag_gets_previous_punchline_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Tag.", "label": "tag", "bit": None, "beat": None},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertEqual(cleaned["lines"][1]["bit"], 1)
        self.assertEqual(cleaned["lines"][1]["beat"], 1)

    def test_fluff_inside_beat_can_be_inferred_from_punchline_anchor(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertEqual(cleaned["lines"][1]["bit"], 1)
        self.assertEqual(cleaned["lines"][1]["beat"], 1)

    def test_fluff_between_beats_gets_bit_and_null_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "A", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Reset.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "B", "label": "punchline", "bit": 1, "beat": 2},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertEqual(cleaned["lines"][1]["bit"], 1)
        self.assertIsNone(cleaned["lines"][1]["beat"])

    def test_fluff_inside_beat_gets_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertEqual(cleaned["lines"][1]["bit"], 1)
        self.assertEqual(cleaned["lines"][1]["beat"], 1)

    def test_fluff_outside_bit_stays_null(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Intro.", "label": "fluff", "bit": 9, "beat": 9},
                {"line_number": 2, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 4, "text": "Thanks.", "label": "fluff", "bit": 9, "beat": 9},
            ],
        }

        cleaned = clean_fluff_bit_beat(meta)

        self.assertIsNone(cleaned["lines"][0]["bit"])
        self.assertIsNone(cleaned["lines"][0]["beat"])
        self.assertIsNone(cleaned["lines"][3]["bit"])
        self.assertIsNone(cleaned["lines"][3]["beat"])

    def test_cleaner_does_not_mutate_original_meta(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        clean_fluff_bit_beat(meta)

        self.assertIsNone(meta["lines"][1]["bit"])
        self.assertIsNone(meta["lines"][1]["beat"])


class ValidateBitMetaTests(SimpleTestCase):
    def test_contradiction_joke_type_is_valid(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["beats"]["1"] = {
            "premise": "Financial responsibility conflicts with payday loans because both cannot comfortably be true.",
            "joke_type": "contradiction",
            "topics": ["payday loans"],
        }

        validate_bit_meta(meta)

    def test_non_fluff_line_requires_bit_and_beat(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": None,
                "beat": None,
            }
        )

        with self.assertRaisesRegex(
            ValueError, "line 10: 'punchline' lines must have bit and beat values"
        ):
            validate_bit_meta(meta)

    def test_fluff_line_can_have_null_bit_and_beat(self):
        meta = {
            "bit_meta": {},
            "lines": [
                {
                    "line_number": 10,
                    "text": "Thank you.",
                    "label": "fluff",
                    "bit": None,
                    "beat": None,
                }
            ],
        }

        validate_bit_meta(meta)

    def test_non_punchline_line_rejects_bit_and_beat_values(self):
        meta = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another thing.",
                            "joke_type": "reframe",
                            "topics": ["one"],
                        }
                    }
                }
            },
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(
            ValueError,
            "line 1: 'setup' lines must leave bit and beat null",
        ):
            validate_bit_meta(meta)

    def test_tag_must_follow_punchline_or_tag(self):
        meta = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another thing.",
                            "joke_type": "reframe",
                            "topics": ["one"],
                        }
                    }
                }
            },
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
                {"line_number": 2, "text": "Tag.", "label": "tag", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(
            ValueError,
            "line 2: tag must immediately follow a punchline or tag; previous label is 'setup'",
        ):
            validate_bit_meta(meta)

    def test_multi_beat_bit_requires_summary(self):
        meta = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another thing.",
                            "joke_type": "reframe",
                            "topics": ["one"],
                        },
                        "2": {
                            "premise": "Another thing could be a third thing.",
                            "joke_type": "reframe",
                            "topics": ["two"],
                        },
                    }
                }
            },
            "lines": [
                {"line_number": 1, "text": "A", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "B", "label": "punchline", "bit": 1, "beat": 2},
            ],
        }

        with self.assertRaisesRegex(ValueError, "bit 1: multi-beat bits must have a summary"):
            validate_bit_meta(meta)

    def test_single_beat_bit_rejects_summary(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["summary"] = "Duplicate single-beat summary."

        with self.assertRaisesRegex(ValueError, "bit 1: summary is only allowed on multi-beat bits"):
            validate_bit_meta(meta)

    def test_bit_level_premise_is_rejected(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["premise"] = "Old bit-level field."

        with self.assertRaisesRegex(ValueError, "bit 1: use summary for multi-beat bits, not premise"):
            validate_bit_meta(meta)

    def test_bit_meta_must_be_object_not_array(self):
        meta = {
            "bit_meta": [],
            "lines": [
                {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(
            ValueError,
            "bit_meta must be a JSON object keyed by bit number strings, not an array",
        ):
            validate_bit_meta(meta)

    def test_beats_must_be_object_not_array(self):
        meta = {
            "bit_meta": {"1": {"beats": []}},
            "lines": [
                {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(
            ValueError,
            "bit 1: beats must be a JSON object keyed by beat number strings, not an array",
        ):
            validate_bit_meta(meta)

    def test_punchline_anchor_requires_matching_bit_meta_beat(self):
        meta = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another thing.",
                            "joke_type": "reframe",
                            "topics": ["one"],
                        }
                    }
                }
            },
            "lines": [
                {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 2, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(
            ValueError,
            "line\\(s\\) 1: punchline references bit 2 beat 1, but bit_meta has no matching beat",
        ):
            validate_bit_meta(meta)

    def test_topics_must_have_one_to_four_short_strings(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["beats"]["1"]["topics"] = []

        with self.assertRaisesRegex(ValueError, "bit 1 beat 1: topics must contain 1-4 items, got 0"):
            validate_bit_meta(meta)

from django.test import SimpleTestCase

from pipeline.import_utils.records import _infer_line_ownership
from pipeline.import_utils.validation import validate_bit_meta


def valid_meta_with_line(line):
    return {
        "bit_meta": {
            "1": {
                "beats": {
                    "1": {
                        "premise": "A thing could be an unexpected thing.",
                        "joke_type": "reframe",
                        "subject": "a thing",
                        "reframe": "an unexpected thing",
                        "keys": ["thing"],
                    }
                }
            }
        },
        "lines": [line],
    }


class InferLineOwnershipTests(SimpleTestCase):
    def test_setup_gets_next_punchline_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
                {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[1], (1, 1))

    def test_tag_gets_previous_punchline_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Tag.", "label": "tag", "bit": None, "beat": None},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[2], (1, 1))

    def test_fluff_inside_beat_can_be_inferred_from_punchline_anchor(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[2], (1, 1))

    def test_fluff_between_beats_gets_bit_and_null_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "A", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Reset.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "B", "label": "punchline", "bit": 1, "beat": 2},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[2], (1, None))

    def test_fluff_inside_beat_gets_bit_and_beat(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[2], (1, 1))

    def test_fluff_outside_bit_stays_null(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Intro.", "label": "fluff", "bit": 9, "beat": 9},
                {"line_number": 2, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 4, "text": "Thanks.", "label": "fluff", "bit": 9, "beat": 9},
            ],
        }

        ownership = _infer_line_ownership(meta["lines"])

        self.assertEqual(ownership[1], (None, None))
        self.assertEqual(ownership[4], (None, None))

    def test_inference_does_not_mutate_original_meta(self):
        meta = {
            "lines": [
                {"line_number": 1, "text": "Setup.", "label": "setup", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": None, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        _infer_line_ownership(meta["lines"])

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
            "premise": "Financial responsibility both means avoiding debt and yet includes payday loans.",
            "joke_type": "contradiction",
            "subject": "financial responsibility",
            "a": "means avoiding debt",
            "b": "includes payday loans",
            "keys": ["payday loans"],
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
                            "subject": "one thing",
                            "reframe": "another thing",
                            "keys": ["one"],
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
                            "subject": "one thing",
                            "reframe": "another thing",
                            "keys": ["one"],
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

    def test_multi_beat_bit_is_valid_without_summary(self):
        meta = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another thing.",
                            "joke_type": "reframe",
                            "subject": "one thing",
                            "reframe": "another thing",
                            "keys": ["one"],
                        },
                        "2": {
                            "premise": "Another thing could be a third thing.",
                            "joke_type": "reframe",
                            "subject": "another thing",
                            "reframe": "a third thing",
                            "keys": ["another"],
                        },
                    }
                }
            },
            "lines": [
                {"line_number": 1, "text": "A", "label": "punchline", "bit": 1, "beat": 1},
                {"line_number": 2, "text": "B", "label": "punchline", "bit": 1, "beat": 2},
            ],
        }

        validate_bit_meta(meta)  # should not raise

    def test_single_beat_bit_summary_is_allowed(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["summary"] = "Optional summary on a single-beat bit."

        validate_bit_meta(meta)  # should not raise

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
                            "subject": "one thing",
                            "reframe": "another thing",
                            "keys": ["one"],
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

    def test_keys_must_have_one_to_four_short_strings(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["beats"]["1"]["keys"] = []

        with self.assertRaisesRegex(ValueError, "bit 1 beat 1: keys must contain 1-4 items, got 0"):
            validate_bit_meta(meta)

    def test_non_double_meaning_key_must_not_exceed_three_words(self):
        meta = valid_meta_with_line(
            {
                "line_number": 10,
                "text": "Payoff.",
                "label": "punchline",
                "bit": 1,
                "beat": 1,
            }
        )
        meta["bit_meta"]["1"]["beats"]["1"]["subject"] = "one two three four"
        meta["bit_meta"]["1"]["beats"]["1"]["keys"] = ["one two three four"]

        with self.assertRaisesRegex(
            ValueError,
            "bit 1 beat 1: key 1 is too long; use a short searchable noun phrase",
        ):
            validate_bit_meta(meta)

    def test_double_meaning_key_can_be_longer_than_four_words(self):
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
            "premise": "'In case of fire use stairs' can mean escape or extinguish.",
            "joke_type": "double-meaning",
            "phrase": "in case of fire use stairs",
            "expected": "escape",
            "comic": "extinguish",
            "keys": ["in case of fire use stairs", "extinguish"],
        }

        validate_bit_meta(meta)

    def test_phonetic_match_keys_include_both_words_and_reason(self):
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
            "premise": "'Midget' sounds like 'fidget', and 'fidget' fits because ADHD.",
            "joke_type": "phonetic-match",
            "heard": "midget",
            "reheard": "fidget",
            "reason": "ADHD",
            "keys": ["midget", "fidget", "ADHD"],
        }

        validate_bit_meta(meta)

    def test_hyperbole_keys_include_subject_and_extreme(self):
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
            "premise": "A porn collection becomes so extreme that sperm depletion happens.",
            "joke_type": "hyperbole",
            "subject": "a porn collection",
            "extreme": "sperm depletion",
            "keys": ["porn collection", "sperm depletion"],
        }

        validate_bit_meta(meta)

    def test_analogy_key_omits_helper_verb_from_shared(self):
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
            "premise": "Golf is like marriage because both involve expensive repeated failure.",
            "joke_type": "analogy",
            "a": "golf",
            "b": "marriage",
            "shared": "involve expensive repeated failure",
            "keys": ["golf", "marriage", "expensive repeated failure"],
        }

        validate_bit_meta(meta)

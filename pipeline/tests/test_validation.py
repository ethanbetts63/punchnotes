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

    def test_fluff_inside_beat_rejects_null_beat(self):
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
                {"line_number": 2, "text": "Pause.", "label": "fluff", "bit": 1, "beat": None},
                {"line_number": 3, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
            ],
        }

        with self.assertRaisesRegex(ValueError, "line 2: fluff must be bit=1, beat=1"):
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

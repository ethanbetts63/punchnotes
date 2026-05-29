from django.test import SimpleTestCase

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

    def test_partial_bit_beat_pair_is_invalid(self):
        meta = {
            "bit_meta": {},
            "lines": [
                {
                    "line_number": 10,
                    "text": "Small aside.",
                    "label": "fluff",
                    "bit": 1,
                    "beat": None,
                }
            ],
        }

        with self.assertRaisesRegex(
            ValueError, "line 10: bit and beat must both be set or both be null"
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

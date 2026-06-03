from django.test import SimpleTestCase

from pipeline.management.commands.replace_topics_with_empty_keys import replace_topics_with_empty_keys


class ReplaceTopicsWithEmptyKeysTests(SimpleTestCase):
    def test_replaces_beat_topics_with_empty_keys(self):
        data = {
            "bit_meta": {
                "1": {
                    "beats": {
                        "1": {
                            "premise": "One thing could be another.",
                            "joke_type": "reframe",
                            "topics": ["old", "topics"],
                        },
                        "2": {
                            "premise": "Another thing could be third.",
                            "joke_type": "reframe",
                            "keys": ["existing"],
                        },
                    }
                }
            },
            "lines": [
                {
                    "line_number": 1,
                    "text": "I wanna switch topics.",
                    "label": "setup",
                    "bit": None,
                    "beat": None,
                }
            ],
        }

        changed = replace_topics_with_empty_keys(data)

        self.assertEqual(changed, 1)
        self.assertNotIn("topics", data["bit_meta"]["1"]["beats"]["1"])
        self.assertEqual(data["bit_meta"]["1"]["beats"]["1"]["keys"], [])
        self.assertEqual(data["bit_meta"]["1"]["beats"]["2"]["keys"], ["existing"])
        self.assertEqual(data["lines"][0]["text"], "I wanna switch topics.")

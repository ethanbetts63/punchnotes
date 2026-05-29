from django.test import SimpleTestCase

from pipeline.import_utils.transcript_windows import build_transcript_windows


class TranscriptWindowTests(SimpleTestCase):
    def test_windows_start_before_music_and_end_at_next_music(self):
        doc = {
            "video_id": "abc123",
            "lines": [
                {"line_number": i, "text": f"line {i}", "start": i}
                for i in range(1, 101)
            ],
        }
        doc["lines"][39]["text"] = "(upbeat music)"  # line 40
        doc["lines"][79]["text"] = "(upbeat music)"  # line 80

        windows = build_transcript_windows(doc, overlap=25)

        self.assertEqual(len(windows), 2)
        self.assertEqual(windows[0]["window_start_line"], 15)
        self.assertEqual(windows[0]["music_cue_line"], 40)
        self.assertEqual(windows[0]["window_end_line"], 80)
        self.assertEqual(windows[0]["window_number"], 1)
        self.assertEqual(windows[1]["window_start_line"], 55)
        self.assertEqual(windows[1]["music_cue_line"], 80)
        self.assertEqual(windows[1]["window_end_line"], 100)
        self.assertEqual(windows[1]["window_number"], 2)

    def test_skips_windows_shorter_than_minimum(self):
        doc = {
            "video_id": "abc123",
            "lines": [
                {"line_number": i, "text": f"line {i}", "start": i}
                for i in range(1, 31)
            ],
        }
        doc["lines"][0]["text"] = "(upbeat music)"
        doc["lines"][1]["text"] = "(upbeat music)"
        doc["lines"][10]["text"] = "(upbeat music)"

        windows = build_transcript_windows(doc, overlap=25, min_lines=20)

        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["window_number"], 1)
        self.assertEqual(windows[0]["window_start_line"], 1)
        self.assertEqual(windows[0]["window_end_line"], 30)

    def test_returns_no_windows_without_music_cues(self):
        doc = {
            "video_id": "abc123",
            "lines": [
                {"line_number": 1, "text": "No cue here.", "start": 1},
            ],
        }

        self.assertEqual(build_transcript_windows(doc, overlap=25), [])

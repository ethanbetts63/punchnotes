from django.test import SimpleTestCase

from pipeline.import_utils.transcript_windows import build_transcript_windows


class TranscriptWindowTests(SimpleTestCase):
    def test_windows_start_before_music_and_end_before_next_music(self):
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
        self.assertEqual(windows[0]["window_end_line"], 54)
        self.assertEqual(windows[1]["window_start_line"], 55)
        self.assertEqual(windows[1]["music_cue_line"], 80)
        self.assertEqual(windows[1]["window_end_line"], 100)

    def test_returns_no_windows_without_music_cues(self):
        doc = {
            "video_id": "abc123",
            "lines": [
                {"line_number": 1, "text": "No cue here.", "start": 1},
            ],
        }

        self.assertEqual(build_transcript_windows(doc, overlap=25), [])

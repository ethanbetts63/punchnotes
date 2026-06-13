from django.test import TestCase

from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


class SearchConsistencyTests(TestCase):
    def setUp(self):
        self.comedian = Comedian.objects.create(
            name="Casey Rocket",
            slug="casey-rocket",
            appearance_count=1,
        )
        self.episode = Episode.objects.create(
            video_id="abc123xyz01",
            episode_number=700,
            episode_title="Kill Tony #700",
            episode_url="https://example.com/kt-700",
            set_count=1,
        )
        self.set_obj = Set.objects.create(
            episode=self.episode,
            comedian=self.comedian,
            set_number=1,
            start_seconds=0,
            bit_count=1,
        )
        self.bit = Bit.objects.create(
            set=self.set_obj,
            bit_id="b1",
            summary="A rocket joke",
            line_start=1,
            line_end=2,
        )
        self.beat = Beat.objects.create(
            bit=self.bit,
            beat_id="beat-1",
            line_start=1,
            line_end=3,
            premise="A clean premise",
            joke_type="misdirect",
        )
        Line.objects.create(
            set=self.set_obj,
            line_number=1,
            label="setup",
            text="hello there",
            start_seconds=0,
        )
        Line.objects.create(
            set=self.set_obj,
            line_number=2,
            label="fluff",
            text="this fluff line should stay ignored",
            start_seconds=1,
        )
        Line.objects.create(
            set=self.set_obj,
            line_number=3,
            label="punchline",
            text="this line should not make the comedian searchable globally",
            start_seconds=2,
        )

    def test_global_search_does_not_match_comedians_from_transcript_text(self):
        response = self.client.get("/api/killtony/search/", {"q": "hello"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["comedians"], [])
        self.assertEqual(response.json()["beats"][0]["title"], "hello there")
        self.assertEqual(response.json()["beats"][0]["matched_line_label"], "setup")

    def test_global_comedian_bucket_matches_comedian_search_endpoint(self):
        global_response = self.client.get("/api/killtony/search/", {"q": "casey"})
        comedian_response = self.client.get("/api/killtony/comedians/", {"q": "casey"})

        self.assertEqual(global_response.status_code, 200)
        self.assertEqual(comedian_response.status_code, 200)

        global_names = [item["title"] for item in global_response.json()["comedians"]]
        comedian_names = [item["name"] for item in comedian_response.json()]
        self.assertEqual(global_names, comedian_names)

    def test_beat_search_ignores_fluff_lines(self):
        response = self.client.get("/api/killtony/search/", {"q": "ignored"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["beats"], [])

    def test_beat_endpoint_returns_matching_line_for_text_search(self):
        response = self.client.get("/api/killtony/jokes/", {"q": "hello"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], self.beat.id)
        self.assertEqual(payload[0]["matched_line"], "hello there")
        self.assertEqual(payload[0]["matched_line_label"], "setup")

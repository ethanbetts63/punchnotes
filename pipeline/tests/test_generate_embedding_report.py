import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from pipeline.management.commands.generate_embeddings_report import _build_beat_records, fetch_lines_for_beats
from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


class GenerateEmbeddingReportTests(TestCase):
    def _create_set(self, comedian_name, slug, set_number):
        comedian = Comedian.objects.create(name=comedian_name, slug=slug)
        episode = Episode.objects.create(
            video_id=f"video-{slug}",
            episode_title=f"Episode {slug}",
            episode_url=f"https://example.com/{slug}",
        )
        return Set.objects.create(
            episode=episode,
            comedian=comedian,
            set_number=set_number,
            start_seconds=float(set_number * 10),
        )

    def _create_beat(self, standup_set, beat_id, line_start, line_end, premise, embedding):
        bit = Bit.objects.create(
            set=standup_set,
            bit_id=f"bit-{beat_id}",
            line_start=line_start,
            line_end=line_end,
        )
        return Beat.objects.create(
            bit=bit,
            beat_id=beat_id,
            line_start=line_start,
            line_end=line_end,
            premise=premise,
            joke_type="misdirect",
            keys=["key"],
            embedding=embedding,
        )

    def test_fetch_lines_for_beats_batches_line_query(self):
        standup_set = self._create_set("Comic One", "comic-one", 1)
        beat_a = self._create_beat(standup_set, "a", 1, 2, "first premise", [1.0, 0.0])
        beat_b = self._create_beat(standup_set, "b", 3, 4, "second premise", [1.0, 0.0])
        Line.objects.bulk_create([
            Line(set=standup_set, line_number=1, label="setup", text="setup a", start_seconds=1.0),
            Line(set=standup_set, line_number=2, label="punchline", text="punch a", start_seconds=2.0),
            Line(set=standup_set, line_number=3, label="setup", text="setup b", start_seconds=3.0),
            Line(set=standup_set, line_number=4, label="tag", text="tag b", start_seconds=4.0),
            Line(set=standup_set, line_number=5, label="fluff", text="ignore me", start_seconds=5.0),
        ])

        records = _build_beat_records(
            Beat.objects.filter(id__in=[beat_a.id, beat_b.id]).select_related("bit__set__comedian")
        )

        with CaptureQueriesContext(connection) as queries:
            lines_by_beat = fetch_lines_for_beats(records)

        self.assertEqual(len(queries), 1)
        self.assertEqual(lines_by_beat[beat_a.id], [
            {"label": "setup", "text": "setup a"},
            {"label": "punchline", "text": "punch a"},
        ])
        self.assertEqual(lines_by_beat[beat_b.id], [
            {"label": "setup", "text": "setup b"},
            {"label": "tag", "text": "tag b"},
        ])

    def test_command_writes_expected_pairs_with_wrapped_report(self):
        set_a = self._create_set("Comic One", "comic-one", 1)
        set_b = self._create_set("Comic Two", "comic-two", 1)
        beat_a = self._create_beat(set_a, "a", 1, 2, "premise a", [1.0, 0.0])
        beat_b = self._create_beat(set_b, "b", 1, 2, "premise b", [1.0, 0.0])
        Line.objects.bulk_create([
            Line(set=set_a, line_number=1, label="setup", text="setup a", start_seconds=1.0),
            Line(set=set_a, line_number=2, label="punchline", text="punch a", start_seconds=2.0),
            Line(set=set_b, line_number=1, label="setup", text="setup b", start_seconds=1.0),
            Line(set=set_b, line_number=2, label="punchline", text="punch b", start_seconds=2.0),
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(PIPELINE_DATA_DIR=Path(tmpdir)):
                stdout = StringIO()
                call_command("generate_embeddings_report", stdout=stdout)

                report_path = Path(tmpdir) / "embedding_similarity_report.json"
                payload = json.loads(report_path.read_text(encoding="utf-8"))

                self.assertIn("generated_at", payload)
                self.assertEqual(payload["threshold"], 0.70)
                self.assertEqual(len(payload["pairs"]), 1)
                pair = payload["pairs"][0]
                self.assertEqual(pair["similarity"], 1.0)
                self.assertEqual({pair["beat_a"]["id"], pair["beat_b"]["id"]}, {beat_a.id, beat_b.id})
                self.assertIn("Stored 1 total pairs", stdout.getvalue())

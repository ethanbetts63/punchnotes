import types
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from pipeline.management.commands.generate_embeddings import _embedding_text, _load_lines_by_set
from pipeline.models import Beat, Bit, Comedian, Episode, Line, Set


class GenerateEmbeddingsTests(TestCase):
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

    def _create_beat(self, standup_set, beat_id, line_start, line_end, embedding=None):
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
            premise=f"premise {beat_id}",
            joke_type="misdirect",
            keys=["key"],
            embedding=[] if embedding is None else embedding,
        )

    def test_embedding_text_supports_structured_format(self):
        standup_set = self._create_set("Comic One", "comic-one", 1)
        beat = self._create_beat(standup_set, "a", 1, 3)
        Line.objects.bulk_create([
            Line(set=standup_set, line_number=1, label="setup", text="setup one", start_seconds=1.0),
            Line(set=standup_set, line_number=2, label="setup", text="setup two", start_seconds=2.0),
            Line(set=standup_set, line_number=3, label="punchline", text="punch", start_seconds=3.0),
        ])

        self.assertEqual(
            _embedding_text(beat),
            "setup one setup two punch",
        )
        self.assertEqual(
            _embedding_text(beat, text_format="structured"),
            "Setup: setup one setup two\nPunchline: punch",
        )

    def test_load_lines_by_set_batches_line_lookup_once(self):
        standup_set = self._create_set("Comic One", "comic-one", 1)
        beat_a = self._create_beat(standup_set, "a", 1, 2)
        beat_b = self._create_beat(standup_set, "b", 3, 4)
        Line.objects.bulk_create([
            Line(set=standup_set, line_number=1, label="setup", text="setup one", start_seconds=1.0),
            Line(set=standup_set, line_number=2, label="punchline", text="punch one", start_seconds=2.0),
            Line(set=standup_set, line_number=3, label="setup", text="setup two", start_seconds=3.0),
            Line(set=standup_set, line_number=4, label="punchline", text="punch two", start_seconds=4.0),
        ])

        with self.assertNumQueries(1):
            lines_by_set = _load_lines_by_set([beat_a, beat_b])

        self.assertEqual(
            _embedding_text(beat_a, lines_by_set=lines_by_set),
            "setup one punch one",
        )
        self.assertEqual(
            _embedding_text(beat_b, lines_by_set=lines_by_set, text_format="structured"),
            "Setup: setup two\nPunchline: punch two",
        )

    def test_command_can_overwrite_existing_embeddings_with_structured_text(self):
        standup_set = self._create_set("Comic One", "comic-one", 1)
        beat = self._create_beat(standup_set, "a", 1, 2, embedding=[9.0, 9.0])
        Line.objects.bulk_create([
            Line(set=standup_set, line_number=1, label="setup", text="setup text", start_seconds=1.0),
            Line(set=standup_set, line_number=2, label="punchline", text="punch text", start_seconds=2.0),
        ])

        captured = {}

        class FakeSentenceTransformer:
            def __init__(self, model_name):
                captured["model_name"] = model_name

            def encode(self, texts, batch_size, show_progress_bar):
                captured["texts"] = list(texts)
                return types.SimpleNamespace(tolist=lambda: [[1.0, 2.0] for _ in texts])

        fake_sentence_transformers = types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)

        stdout = StringIO()
        with patch.dict(
            "sys.modules",
            {
                "sentence_transformers": fake_sentence_transformers,
            },
        ):
            call_command(
                "generate_embeddings",
                "--text-format=structured",
                "--overwrite",
                stdout=stdout,
            )

        beat.refresh_from_db()
        self.assertEqual(beat.embedding, [1.0, 2.0])
        self.assertEqual(captured["texts"], ["Setup: setup text\nPunchline: punch text"])
        self.assertIn("using structured text", stdout.getvalue())
        self.assertIn("Loading all-mpnet-base-v2...", stdout.getvalue())

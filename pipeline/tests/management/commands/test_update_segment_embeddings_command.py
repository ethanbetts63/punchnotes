import pytest
from django.core.management import call_command


pytestmark = pytest.mark.django_db


def test_update_segment_embeddings_flag_dispatches(monkeypatch):
    import pipeline.utils.update.segment_embeddings as module

    called = {}

    def fake_run(log):
        called["ran"] = True

    monkeypatch.setattr(module, "run_update_segment_embeddings", fake_run)

    # --archive is accepted by the command for other tasks, but segment embeddings
    # are never archived, so it must not be forwarded.
    call_command("update", segment_embeddings=True, archive=True)

    assert called == {"ran": True}

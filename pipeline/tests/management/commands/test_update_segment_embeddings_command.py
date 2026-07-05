import pytest
from django.core.management import call_command


pytestmark = pytest.mark.django_db


def test_update_segment_embeddings_flag_dispatches(monkeypatch):
    import pipeline.utils.update.segment_embeddings as module

    called = {}

    def fake_run(log, archive=False):
        called["archive"] = archive

    monkeypatch.setattr(module, "run_update_segment_embeddings", fake_run)

    call_command("update", segment_embeddings=True, archive=True)

    assert called == {"archive": True}

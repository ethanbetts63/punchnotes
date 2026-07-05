import pytest
from django.core.management import call_command


pytestmark = pytest.mark.django_db


def test_reset_db_restores_segment_embeddings_from_archive(tmp_path, settings, monkeypatch):
    archive_dir = tmp_path / "private" / "segment_embeddings_archive"
    archive_dir.mkdir(parents=True)
    (archive_dir / "segment_embeddings.jsonl").write_text('{"key": "x", "embedding": [1.0]}\n', encoding="utf-8")

    settings.BASE_DIR = tmp_path
    settings.PIPELINE_DATA_DIR = tmp_path / "data"
    settings.PIPELINE_PRIVATE_DATA_DIR = tmp_path / "private"
    settings.PIPELINE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (tmp_path / "pipeline" / "migrations").mkdir(parents=True, exist_ok=True)
    (tmp_path / "mediafiles").mkdir(parents=True, exist_ok=True)
    settings.MEDIA_ROOT = tmp_path / "mediafiles"

    calls = []
    monkeypatch.setattr(
        "pipeline.management.commands.reset_db.call_command",
        lambda name, **kwargs: calls.append((name, kwargs)),
    )
    monkeypatch.setattr("pipeline.management.commands.reset_db.connection", type("C", (), {
        "cursor": lambda self: __import__("contextlib").nullcontext(type("Cur", (), {
            "execute": lambda self, sql: None,
        })()),
        "introspection": type("I", (), {"table_names": lambda self, cursor: []})(),
    })())

    call_command("reset_db")

    assert ("update", {"segment_embeddings": True, "archive": True}) in calls

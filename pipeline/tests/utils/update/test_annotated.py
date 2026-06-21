import pytest
from django.core.management import call_command
from django.test import override_settings

from pipeline.utils.update.annotated import ingest_annotated_set
from pipeline.utils.update import annotated_archive


pytestmark = pytest.mark.django_db


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def test_ingest_annotated_set_requires_existing_video():
    data = {
        "video_id": "missing123",
        "comedian_name": "Test Comic",
        "start_seconds": 10,
        "lines": [
            {"line_number": 1, "text": "Setup.", "label": "setup", "bit": None, "beat": None},
            {"line_number": 2, "text": "Payoff.", "label": "punchline", "bit": 1, "beat": 1},
        ],
        "bit_meta": {
            "1": {
                "beats": {
                    "1": {
                        "premise": "A setup could be a payoff.",
                        "joke_type": "reframe",
                        "subject": "a setup",
                        "reframe": "a payoff",
                    }
                }
            }
        },
    }

    with pytest.raises(ValueError, match="Run update --ep_meta"):
        ingest_annotated_set(data)


def test_update_annotated_sets_alias_passes_archive(monkeypatch):
    calls = []

    def fake_run_update_annotated(log, archive=False):
        calls.append(archive)

    monkeypatch.setattr(annotated_archive, "run_update_annotated", fake_run_update_annotated)

    call_command("update", "--annotated_sets", "--archive")

    assert calls == [True]


def test_run_update_annotated_archive_reads_private_archive_without_moving(tmp_path, monkeypatch):
    public_dir = tmp_path / "data"
    private_dir = tmp_path / "data_private"
    archive_dir = private_dir / "bit_annotated_set_archive"
    archive_dir.mkdir(parents=True)
    source_file = archive_dir / "set.json"
    source_file.write_text('{"comedian_name": "Test Comic", "lines": []}', encoding="utf-8")
    imported = []

    def fake_ingest(data, relationships, defer_refresh=False):
        imported.append((data, relationships, defer_refresh))
        return {"comedian": data["comedian_name"], "lines": 0, "bits": 0}

    monkeypatch.setattr(annotated_archive, "load_relationships", lambda: {"aliases": {}})
    monkeypatch.setattr(annotated_archive, "ingest_annotated_set", fake_ingest)
    monkeypatch.setattr(annotated_archive, "refresh_all_stats", lambda: None)

    with override_settings(PIPELINE_DATA_DIR=public_dir, PIPELINE_PRIVATE_DATA_DIR=private_dir):
        annotated_archive.run_update_annotated(CapturingLog(), archive=True)

    assert imported == [({"comedian_name": "Test Comic", "lines": []}, {"aliases": {}}, True)]
    assert source_file.exists()
    assert not (public_dir / "annotated_set_inbox" / "set.json").exists()

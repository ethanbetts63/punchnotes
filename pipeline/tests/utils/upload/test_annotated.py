from django.test import override_settings

from pipeline.utils.upload import annotated


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def _valid_annotation():
    return """{
  "video_id": "abc123",
  "comedian_name": "Test Comic",
  "lines": []
}
"""


def test_validate_annotated_files_partitions_valid_and_invalid(tmp_path):
    valid = tmp_path / "valid.json"
    invalid = tmp_path / "invalid.json"
    valid.write_text(_valid_annotation(), encoding="utf-8")
    invalid.write_text('{"video_id": "abc123", "comedian_name": "Test Comic", "lines": "bad"}', encoding="utf-8")
    log = CapturingLog()

    valid_paths, invalid_paths = annotated.validate_annotated_files([valid, invalid], log)

    assert valid_paths == [valid]
    assert invalid_paths == [invalid]
    assert "validation failed" in log.messages[0]


def test_upload_annotated_zips_and_archives_only_valid_files(tmp_path, monkeypatch):
    source_dir = tmp_path / "2_set_inbox"
    source_dir.mkdir()
    valid = source_dir / "valid.json"
    invalid = source_dir / "invalid.json"
    valid.write_text(_valid_annotation(), encoding="utf-8")
    invalid.write_text('{"video_id": "abc123", "comedian_name": "Test Comic", "lines": "bad"}', encoding="utf-8")
    uploaded_paths = []

    def fake_upload(paths, log):
        uploaded_paths.extend(paths)
        return True

    monkeypatch.setattr(annotated, "upload_annotated_files", fake_upload)
    log = CapturingLog()

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        annotated.upload_annotated({"file": None, "dir": str(source_dir)}, log)

    assert uploaded_paths == [valid]
    assert not valid.exists()
    assert (tmp_path / "bit_annotated_set_archive" / "valid.json").exists()
    assert invalid.exists()
    assert not (tmp_path / "bit_annotated_set_archive" / "invalid.json").exists()
    assert log.messages[-1] == "\n1 uploaded, 1 failed."

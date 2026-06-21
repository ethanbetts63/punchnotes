from django.test import override_settings

from pipeline.utils.upload import set_images


class CapturingLog:
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)


def test_upload_set_images_archives_outbox_files_after_upload(tmp_path, monkeypatch):
    outbox_dir = tmp_path / "set_images_outbox"
    outbox_dir.mkdir()
    image = outbox_dir / "KT001_set01_test.jpg"
    image.write_bytes(b"image")
    uploaded_batches = []

    monkeypatch.setattr(set_images, "pipeline_session", lambda: object())
    monkeypatch.setattr(set_images, "_upload_batch", lambda session, paths, log: uploaded_batches.append(paths) or paths)
    log = CapturingLog()

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        set_images.upload_set_images({"archive": False}, log)

    archived = tmp_path / "set_images_archive" / image.name
    assert uploaded_batches == [[image]]
    assert archived.exists()
    assert not image.exists()
    assert log.messages[-1] == "Done. 1 uploaded, 0 failed."


def test_upload_set_images_archive_uploads_without_moving_files(tmp_path, monkeypatch):
    archive_dir = tmp_path / "set_images_archive"
    archive_dir.mkdir()
    image = archive_dir / "KT001_set01_test.jpg"
    image.write_bytes(b"image")
    uploaded_batches = []

    monkeypatch.setattr(set_images, "pipeline_session", lambda: object())
    monkeypatch.setattr(set_images, "_upload_batch", lambda session, paths, log: uploaded_batches.append(paths) or paths)
    log = CapturingLog()

    with override_settings(PIPELINE_DATA_DIR=tmp_path):
        set_images.upload_set_images({"archive": True}, log)

    assert uploaded_batches == [[image]]
    assert image.exists()
    assert log.messages[-1] == "Done. 1 uploaded, 0 failed."

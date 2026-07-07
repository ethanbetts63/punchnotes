import pytest
from django.test import override_settings

from pipeline.models import Comedian, Set, Video
from pipeline.log import Log


pytestmark = pytest.mark.django_db


class SilentLog(Log):
    def __init__(self):
        self.messages = []

    def __call__(self, msg):
        self.messages.append(msg)

    def success(self, msg):
        self.messages.append(msg)

    def error(self, msg):
        self.messages.append(msg)

    def warning(self, msg):
        self.messages.append(msg)


def _make_video(number):
    return Video.objects.create(
        video_id=f"testvid{number:04d}",
        number=number,
        title=f"KT #{number} - Test",
        url=f"https://www.youtube.com/watch?v=testvid{number:04d}",
    )


def _make_set(video, slug, name, start_seconds, image_url=None):
    comedian, _ = Comedian.objects.get_or_create(slug=slug, defaults={"name": name})
    s = Set.objects.create(video=video, comedian=comedian, start_seconds=start_seconds)
    if image_url:
        s.image_url = image_url
        s.save(update_fields=["image_url"])
    return s


def test_renames_legacy_public_and_archive_files(tmp_path):
    from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images

    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(765)
    s = _make_set(video, "karen-feehan", "Karen Feehan", 142.0, image_url="set-images/KT765_set06_karen-feehan.jpg")
    (public_dir / "KT765_set06_karen-feehan.jpg").write_bytes(b"img")
    (archive_dir / "KT765_set06_karen-feehan.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        rename_legacy_set_images(SilentLog())

    s.refresh_from_db()
    assert s.image_url == "set-images/KT765_142_karen-feehan.jpg"
    assert (public_dir / "KT765_142_karen-feehan.jpg").exists()
    assert not (public_dir / "KT765_set06_karen-feehan.jpg").exists()
    assert (archive_dir / "KT765_142_karen-feehan.jpg").exists()
    assert not (archive_dir / "KT765_set06_karen-feehan.jpg").exists()


def test_updates_comedian_cached_image_url(tmp_path):
    from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images

    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(765)
    s = _make_set(video, "karen-feehan", "Karen Feehan", 142.0, image_url="set-images/KT765_set06_karen-feehan.jpg")
    s.comedian.image_url = "set-images/KT765_set06_karen-feehan.jpg"
    s.comedian.image_set = s
    s.comedian.save(update_fields=["image_url", "image_set"])
    (public_dir / "KT765_set06_karen-feehan.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        rename_legacy_set_images(SilentLog())

    s.comedian.refresh_from_db()
    assert s.comedian.image_url == "set-images/KT765_142_karen-feehan.jpg"


def test_skips_files_already_in_new_format(tmp_path):
    from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images

    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(766)
    s = _make_set(video, "david-jolly", "David Jolly", 100.0, image_url="set-images/KT766_100_david-jolly.jpg")
    (public_dir / "KT766_100_david-jolly.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        rename_legacy_set_images(SilentLog())

    s.refresh_from_db()
    assert s.image_url == "set-images/KT766_100_david-jolly.jpg"
    assert (public_dir / "KT766_100_david-jolly.jpg").exists()


def test_dry_run_does_not_touch_files_or_db(tmp_path):
    from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images

    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(765)
    s = _make_set(video, "karen-feehan", "Karen Feehan", 142.0, image_url="set-images/KT765_set06_karen-feehan.jpg")
    (public_dir / "KT765_set06_karen-feehan.jpg").write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        rename_legacy_set_images(SilentLog(), dry_run=True)

    s.refresh_from_db()
    assert s.image_url == "set-images/KT765_set06_karen-feehan.jpg"
    assert (public_dir / "KT765_set06_karen-feehan.jpg").exists()
    assert not (public_dir / "KT765_142_karen-feehan.jpg").exists()


def test_warns_on_unparseable_filename(tmp_path):
    from pipeline.utils.fix.rename_legacy_set_images import rename_legacy_set_images

    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(765)
    s = _make_set(video, "karen-feehan", "Karen Feehan", 142.0, image_url="set-images/not-a-real-name.jpg")

    log = SilentLog()
    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        rename_legacy_set_images(log)

    s.refresh_from_db()
    assert s.image_url == "set-images/not-a-real-name.jpg"
    assert any("not-a-real-name.jpg" in msg for msg in log.messages)

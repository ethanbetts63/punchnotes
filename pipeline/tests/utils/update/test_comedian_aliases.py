import pytest
from django.test import override_settings

from pipeline.models import Comedian, Set, Video
from pipeline.utils.comedian_aliases import empty_relationships
from pipeline.utils.update.comedian_aliases import dedup_comedians
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


def _make_comedian(slug, name):
    return Comedian.objects.create(slug=slug, name=name)


def _make_video(number):
    return Video.objects.create(
        video_id=f"testvid{number:04d}",
        number=number,
        title=f"KT #{number} - Test",
        url=f"https://www.youtube.com/watch?v=testvid{number:04d}",
    )


def _make_set(video, comedian, set_number, image_url=None):
    s = Set.objects.create(video=video, comedian=comedian, set_number=set_number, start_seconds=0)
    if image_url:
        s.image_url = image_url
        s.save(update_fields=["image_url"])
    return s


def _alias(alias_slug, canonical_slug, canonical_name):
    r = empty_relationships()
    r["aliases"][alias_slug] = {"canonical_slug": canonical_slug, "canonical_name": canonical_name}
    return r


# --- rename path (canonical does not yet exist) ---

def test_rename_path_renames_image_files(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(1)
    alias_comic = _make_comedian("dedric-flynn", "Dedric Flynn")
    _make_set(video, alias_comic, set_number=1, image_url="set-images/KT1_set01_dedric-flynn.jpg")
    (public_dir / "KT1_set01_dedric-flynn.jpg").write_bytes(b"img")
    (archive_dir / "KT1_set01_dedric-flynn.jpg").write_bytes(b"img")

    relationships = _alias("dedric-flynn", "dedrick-flynn", "Dedrick Flynn")
    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        dedup_comedians(relationships, SilentLog())

    comedian = Comedian.objects.get(slug="dedrick-flynn")
    s = Set.objects.get(comedian=comedian)
    assert s.image_url == "set-images/KT1_set01_dedrick-flynn.jpg"
    assert (public_dir / "KT1_set01_dedrick-flynn.jpg").exists()
    assert not (public_dir / "KT1_set01_dedric-flynn.jpg").exists()
    assert (archive_dir / "KT1_set01_dedrick-flynn.jpg").exists()
    assert not (archive_dir / "KT1_set01_dedric-flynn.jpg").exists()


def test_rename_path_handles_set_with_no_image(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    public_dir.mkdir(parents=True)
    (tmp_path / "pipeline" / "set_images_archive").mkdir(parents=True)

    video = _make_video(1)
    alias_comic = _make_comedian("dedric-flynn", "Dedric Flynn")
    _make_set(video, alias_comic, set_number=1)

    relationships = _alias("dedric-flynn", "dedrick-flynn", "Dedrick Flynn")
    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        dedup_comedians(relationships, SilentLog())

    comedian = Comedian.objects.get(slug="dedrick-flynn")
    s = Set.objects.get(comedian=comedian)
    assert s.image_url is None


# --- merge path (canonical already exists) ---

def test_merge_path_renames_image_files(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video = _make_video(1)
    alias_comic = _make_comedian("dedric-flynn", "Dedric Flynn")
    canonical_comic = _make_comedian("dedrick-flynn", "Dedrick Flynn")
    _make_set(video, alias_comic, set_number=1, image_url="set-images/KT1_set01_dedric-flynn.jpg")
    (public_dir / "KT1_set01_dedric-flynn.jpg").write_bytes(b"img")
    (archive_dir / "KT1_set01_dedric-flynn.jpg").write_bytes(b"img")

    relationships = _alias("dedric-flynn", "dedrick-flynn", "Dedrick Flynn")
    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        dedup_comedians(relationships, SilentLog())

    s = Set.objects.get(comedian=canonical_comic)
    assert s.image_url == "set-images/KT1_set01_dedrick-flynn.jpg"
    assert (public_dir / "KT1_set01_dedrick-flynn.jpg").exists()
    assert not (public_dir / "KT1_set01_dedric-flynn.jpg").exists()
    assert (archive_dir / "KT1_set01_dedrick-flynn.jpg").exists()
    assert not (archive_dir / "KT1_set01_dedric-flynn.jpg").exists()
    assert not Comedian.objects.filter(slug="dedric-flynn").exists()


def test_merge_path_renames_multiple_sets(tmp_path):
    public_dir = tmp_path / "media" / "set-images"
    archive_dir = tmp_path / "pipeline" / "set_images_archive"
    public_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)

    video1 = _make_video(1)
    video2 = _make_video(2)
    alias_comic = _make_comedian("dedric-flynn", "Dedric Flynn")
    canonical_comic = _make_comedian("dedrick-flynn", "Dedrick Flynn")

    _make_set(video1, alias_comic, set_number=1, image_url="set-images/KT1_set01_dedric-flynn.jpg")
    _make_set(video2, alias_comic, set_number=3, image_url="set-images/KT2_set03_dedric-flynn.jpg")
    (public_dir / "KT1_set01_dedric-flynn.jpg").write_bytes(b"img")
    (public_dir / "KT2_set03_dedric-flynn.jpg").write_bytes(b"img")

    relationships = _alias("dedric-flynn", "dedrick-flynn", "Dedrick Flynn")
    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path / "pipeline"):
        dedup_comedians(relationships, SilentLog())

    urls = set(Set.objects.filter(comedian=canonical_comic).values_list("image_url", flat=True))
    assert urls == {
        "set-images/KT1_set01_dedrick-flynn.jpg",
        "set-images/KT2_set03_dedrick-flynn.jpg",
    }
    assert (public_dir / "KT1_set01_dedrick-flynn.jpg").exists()
    assert (public_dir / "KT2_set03_dedrick-flynn.jpg").exists()

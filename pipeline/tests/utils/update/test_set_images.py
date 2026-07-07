import pytest
from django.test import override_settings

from pipeline.models import Comedian, Set, Video
from pipeline.utils.update.set_images import ingest_set_image


pytestmark = pytest.mark.django_db


def _make_episode(tmp_path, number=1):
    return Video.objects.create(
        video_id="testvid0001",
        number=number,
        title=f"KT #{number} - Test",
        url="https://www.youtube.com/watch?v=testvid0001",
    )


def _make_set(video, slug, name, start_seconds=0):
    comedian, _ = Comedian.objects.get_or_create(slug=slug, defaults={"name": name})
    return Set.objects.create(video=video, comedian=comedian, start_seconds=start_seconds)


def test_ingest_set_image_rejects_mismatched_comedian_slug(tmp_path):
    episode = _make_episode(tmp_path, number=1)
    _make_set(episode, "real-comic", "Real Comic", start_seconds=100)

    inbox = tmp_path / "set_images_inbox"
    inbox.mkdir()
    image = inbox / "KT1_100_wrong-comic.jpg"
    image.write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path):
        with pytest.raises(ValueError, match="Comedian slug mismatch"):
            ingest_set_image(image)


def test_ingest_set_image_accepts_matching_comedian_slug(tmp_path):
    episode = _make_episode(tmp_path, number=1)
    _make_set(episode, "real-comic", "Real Comic", start_seconds=100)

    inbox = tmp_path / "set_images_inbox"
    inbox.mkdir()
    image = inbox / "KT1_100_real-comic.jpg"
    image.write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path):
        result = ingest_set_image(image)

    assert result == "imported"


def test_ingest_set_image_matches_by_truncated_start_seconds(tmp_path):
    episode = _make_episode(tmp_path, number=1)
    _make_set(episode, "real-comic", "Real Comic", start_seconds=100.7)

    inbox = tmp_path / "set_images_inbox"
    inbox.mkdir()
    image = inbox / "KT1_100_real-comic.jpg"
    image.write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path):
        result = ingest_set_image(image)

    assert result == "imported"


def test_ingest_set_image_skips_when_image_already_exists(tmp_path):
    episode = _make_episode(tmp_path, number=1)
    s = _make_set(episode, "real-comic", "Real Comic", start_seconds=100)
    s.image_url = "set-images/KT1_100_real-comic.jpg"
    s.save(update_fields=["image_url"])

    inbox = tmp_path / "set_images_inbox"
    inbox.mkdir()
    image = inbox / "KT1_100_real-comic.jpg"
    image.write_bytes(b"img")

    with override_settings(MEDIA_ROOT=tmp_path / "media", PIPELINE_DATA_DIR=tmp_path):
        result = ingest_set_image(image)

    assert result == "skipped"

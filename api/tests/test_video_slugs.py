import pytest

from api.video_slugs import lookup_video_by_public_slug, video_public_slug
from pipeline.models import Video


pytestmark = pytest.mark.django_db


def test_video_whose_id_starts_with_a_hyphen_round_trips():
    video = Video.objects.create(video_id="-exshTWEHRQ", number=319, title="Kill Tony #319 - Steveo", url="https://example.com/319")
    slug = video_public_slug(video)
    assert slug == "kill-tony-319-steveo---exshTWEHRQ"
    assert list(lookup_video_by_public_slug(slug)) == [video]


def test_video_whose_id_contains_a_hyphen_round_trips():
    video = Video.objects.create(video_id="tXW0SFv1C-U", number=751, title="KT #751 - Joe Rogan", url="https://example.com/751")
    assert list(lookup_video_by_public_slug(video_public_slug(video))) == [video]

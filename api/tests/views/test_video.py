import pytest

from pipeline.models import Comedian, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def two_videos(db):
    v1 = Video.objects.create(video_id="aaa0000001", number=700, title="Kill Tony #700", url="https://example.com/700", bucket_pull_count=2)
    v2 = Video.objects.create(video_id="bbb0000002", number=701, title="Kill Tony #701 - Special", url="https://example.com/701", golden_ticket_count=1)
    return v1, v2


def test_episode_list_returns_200(client, two_videos):
    resp = client.get("/api/killtony/episodes/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_episode_list_title_search(client, two_videos):
    resp = client.get("/api/killtony/episodes/", {"q": "Special"})
    assert resp.status_code == 200
    titles = [e["title"] for e in resp.json()]
    assert titles == ["Kill Tony #701 - Special"]


def test_episode_list_number_search(client, two_videos):
    resp = client.get("/api/killtony/episodes/", {"q": "700"})
    assert resp.status_code == 200
    numbers = [e["number"] for e in resp.json()]
    assert 700 in numbers


def test_episode_list_kt_prefix_search(client, two_videos):
    resp = client.get("/api/killtony/episodes/", {"q": "KT700"})
    assert resp.status_code == 200
    numbers = [e["number"] for e in resp.json()]
    assert 700 in numbers


def test_episode_list_has_bucket_pull_filter(client, two_videos):
    resp = client.get("/api/killtony/episodes/", {"has": "bucket_pull"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["number"] == 700


def test_episode_list_has_golden_ticket_filter(client, two_videos):
    resp = client.get("/api/killtony/episodes/", {"has": "golden_ticket"})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["number"] == 701


def test_episode_list_sorts_by_like_ratio_ascending(client):
    Video.objects.create(
        video_id="aaa0000001",
        number=700,
        title="Kill Tony #700",
        url="https://example.com/700",
        view_like_ratio=100,
    )
    Video.objects.create(
        video_id="bbb0000002",
        number=701,
        title="Kill Tony #701",
        url="https://example.com/701",
        view_like_ratio=20,
    )
    Video.objects.create(
        video_id="ccc0000003",
        number=702,
        title="Kill Tony #702",
        url="https://example.com/702",
        view_like_ratio=None,
    )

    resp = client.get("/api/killtony/episodes/", {"sort": "like_ratio", "asc": "1"})

    assert resp.status_code == 200
    assert [episode["number"] for episode in resp.json()] == [701, 700, 702]


def test_episode_list_response_shape(client, two_videos):
    resp = client.get("/api/killtony/episodes/")
    episode = resp.json()[0]
    assert "id" in episode
    assert "slug" in episode
    assert "number" in episode
    assert "title" in episode
    assert "youtube_id" in episode


def test_episode_detail_returns_200_by_slug(client, two_videos):
    v1, _ = two_videos
    resp = client.get("/api/killtony/episodes/kill-tony-700--aaa0000001/")
    assert resp.status_code == 200
    assert resp.json()["number"] == 700
    assert resp.json()["id"] == v1.id
    assert resp.json()["slug"] == "kill-tony-700--aaa0000001"


def test_episode_detail_keeps_numeric_id_fallback(client, two_videos):
    v1, _ = two_videos
    resp = client.get(f"/api/killtony/episodes/{v1.id}/")
    assert resp.status_code == 200
    assert resp.json()["slug"] == "kill-tony-700--aaa0000001"


def test_episode_detail_includes_sets(client, db):
    comedian = Comedian.objects.create(name="Test Comic", slug="test-comic")
    video = Video.objects.create(video_id="ccc0000003", number=702, title="Kill Tony #702", url="https://example.com/702")
    Set.objects.create(video=video, comedian=comedian, set_number=1, start_seconds=0)

    resp = client.get("/api/killtony/episodes/kill-tony-702--ccc0000003/")
    assert resp.status_code == 200
    assert len(resp.json()["sets"]) == 1
    assert resp.json()["sets"][0]["comedian"]["name"] == "Test Comic"


def test_episode_detail_404_on_missing(client):
    resp = client.get("/api/killtony/episodes/99999/")
    assert resp.status_code == 404

import pytest

from pipeline.models import Comedian, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def comedian_data(db):
    video = Video.objects.create(video_id="aaa0000001", number=700, title="KT #700", url="https://example.com/700")
    c1 = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", attributes=["man", "regular"], set_count=1, has_large_joke_book=True)
    c2 = Comedian.objects.create(name="Dana Blue", slug="dana-blue", attributes=["woman"], set_count=1)
    no_set = Comedian.objects.create(name="Nobody", slug="nobody")
    Set.objects.create(video=video, comedian=c1, set_number=1, start_seconds=0, attributes=["large_joke_book"])
    Set.objects.create(video=video, comedian=c2, set_number=2, start_seconds=100)
    return c1, c2, no_set


def test_comedian_list_returns_200(client, comedian_data):
    resp = client.get("/api/killtony/comedians/")
    assert resp.status_code == 200


def test_comedian_list_excludes_comedians_without_sets(client, comedian_data):
    resp = client.get("/api/killtony/comedians/")
    names = [c["name"] for c in resp.json()]
    assert "Nobody" not in names
    assert "Casey Rocket" in names


def test_comedian_list_name_search(client, comedian_data):
    resp = client.get("/api/killtony/comedians/", {"q": "casey"})
    names = [c["name"] for c in resp.json()]
    assert names == ["Casey Rocket"]


def test_comedian_list_attribute_filter(client, comedian_data):
    resp = client.get("/api/killtony/comedians/", {"attribute": "woman"})
    names = [c["name"] for c in resp.json()]
    assert names == ["Dana Blue"]
    assert "Casey Rocket" not in names


def test_comedian_list_joke_book_filter(client, comedian_data):
    resp = client.get("/api/killtony/comedians/", {"joke_book": "large"})
    names = [c["name"] for c in resp.json()]
    assert "Casey Rocket" in names
    assert "Dana Blue" not in names


def test_comedian_list_response_shape(client, comedian_data):
    resp = client.get("/api/killtony/comedians/")
    comedian = resp.json()[0]
    assert "id" in comedian
    assert "name" in comedian
    assert "slug" in comedian
    assert "attributes" in comedian
    assert "set_count" in comedian


def test_comedian_detail_returns_200(client, comedian_data):
    c1, _, _ = comedian_data
    resp = client.get(f"/api/killtony/comedians/{c1.slug}/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Casey Rocket"


def test_comedian_detail_includes_sets(client, comedian_data):
    c1, _, _ = comedian_data
    resp = client.get(f"/api/killtony/comedians/{c1.slug}/")
    assert len(resp.json()["sets"]) == 1
    assert resp.json()["sets"][0]["slug"] == "kt700-set01-casey-rocket"


def test_comedian_detail_404_on_missing(client):
    resp = client.get("/api/killtony/comedians/nobody-here/")
    assert resp.status_code == 404

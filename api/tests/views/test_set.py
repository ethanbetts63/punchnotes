import pytest

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def set_data(db):
    video = Video.objects.create(video_id="aaa0000001", number=700, title="KT #700", url="https://example.com/700")
    c1 = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", attributes=["man"])
    c2 = Comedian.objects.create(name="Dana Blue", slug="dana-blue", attributes=["woman"])
    s1 = Set.objects.create(video=video, comedian=c1, set_number=1, start_seconds=0, attributes=["large_joke_book"])
    s2 = Set.objects.create(video=video, comedian=c2, set_number=2, start_seconds=200)
    return video, s1, s2


def test_set_list_returns_200(client, set_data):
    resp = client.get("/api/killtony/sets/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_set_list_search_by_comedian_name(client, set_data):
    resp = client.get("/api/killtony/sets/", {"q": "casey"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["comedian"]["name"] == "Casey Rocket"


def test_set_list_search_does_not_match_video_title(client, set_data):
    resp = client.get("/api/killtony/sets/", {"q": "KT #700"})
    assert len(resp.json()) == 0


def test_set_list_joke_book_filter(client, set_data):
    resp = client.get("/api/killtony/sets/", {"joke_book": "large"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["comedian"]["name"] == "Casey Rocket"


def test_set_list_attribute_filter(client, set_data):
    resp = client.get("/api/killtony/sets/", {"attribute": "woman"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["comedian"]["name"] == "Dana Blue"


def test_set_list_response_shape(client, set_data):
    resp = client.get("/api/killtony/sets/")
    s = resp.json()[0]
    assert "id" in s
    assert s["slug"] == "aaa0000001-set01-casey-rocket"
    assert "set_number" in s
    assert "comedian" in s
    assert "video" in s
    assert "start_seconds" in s


def test_set_detail_returns_200_by_slug(client, set_data):
    _, s1, _ = set_data
    resp = client.get("/api/killtony/sets/aaa0000001-set01-casey-rocket/")
    assert resp.status_code == 200
    assert resp.json()["set_number"] == 1
    assert resp.json()["id"] == s1.id
    assert resp.json()["slug"] == "aaa0000001-set01-casey-rocket"


def test_set_detail_includes_bits_and_lines(client, set_data):
    _, s1, _ = set_data
    bit = Bit.objects.create(set=s1, bit_id="b1", line_start=2, line_end=3)
    Beat.objects.create(bit=bit, beat_id="beat-1", line_start=2, line_end=3, premise="A premise.", joke_type="reframe")
    Line.objects.bulk_create([
        Line(set=s1, line_number=1, label="fluff", text="Intro fluff.", start_seconds=0),
        Line(set=s1, line_number=2, label="setup", text="Setup.", start_seconds=0),
        Line(set=s1, line_number=3, label="punchline", text="Punchline.", start_seconds=1),
    ])

    resp = client.get("/api/killtony/sets/aaa0000001-set01-casey-rocket/")
    data = resp.json()
    assert len(data["bits"]) == 1
    assert len(data["bits"][0]["beats"]) == 1
    assert [line["text"] for line in data["lines"]] == ["Intro fluff.", "Setup.", "Punchline."]
    assert [line["text"] for line in data["bits"][0]["beats"][0]["lines"]] == ["Setup.", "Punchline."]


def test_set_detail_404_on_missing(client):
    resp = client.get("/api/killtony/sets/99999/")
    assert resp.status_code == 404

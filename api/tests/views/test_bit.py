import pytest

from pipeline.models import Beat, Bit, Comedian, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def bit_data(db):
    comedian = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket")
    video = Video.objects.create(video_id="aaa0000001", number=700, title="KT #700", url="https://example.com/700")
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=0)
    bit1 = Bit.objects.create(set=set_obj, bit_id="b1", line_start=1, line_end=2)
    bit2 = Bit.objects.create(set=set_obj, bit_id="b2", line_start=3, line_end=4)
    Beat.objects.create(bit=bit1, beat_id="beat-1", line_start=1, line_end=2, premise="Misdirect premise.", joke_type="misdirect")
    Beat.objects.create(bit=bit2, beat_id="beat-2", line_start=3, line_end=4, premise="Analogy premise.", joke_type="analogy")
    return set_obj, bit1, bit2


def test_bit_list_returns_200(client, bit_data):
    resp = client.get("/api/killtony/bits/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_bit_list_filter_by_joke_type(client, bit_data):
    resp = client.get("/api/killtony/bits/", {"joke_type": "misdirect"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["joke_types"] == ["misdirect"]


def test_bit_list_search_by_premise(client, bit_data):
    resp = client.get("/api/killtony/bits/", {"q": "Analogy"})
    assert len(resp.json()) == 1
    assert resp.json()[0]["joke_types"] == ["analogy"]


def test_bit_list_search_by_comedian_name(client, bit_data):
    resp = client.get("/api/killtony/bits/", {"q": "Casey"})
    assert len(resp.json()) == 2


def test_bit_list_response_shape(client, bit_data):
    resp = client.get("/api/killtony/bits/")
    bit = resp.json()[0]
    assert "id" in bit
    assert "comedian" in bit
    assert "comedian_slug" in bit
    assert "episode_number" in bit
    assert bit["set_slug"] == "aaa0000001-0-casey-rocket"
    assert "joke_types" in bit
    assert "beats" in bit


def test_bit_list_excludes_bits_without_beats(client, db):
    comedian = Comedian.objects.create(name="Empty Comic", slug="empty-comic")
    video = Video.objects.create(video_id="bbb0000002", number=701, title="KT #701", url="https://example.com/701")
    set_obj = Set.objects.create(video=video, comedian=comedian, start_seconds=0)
    Bit.objects.create(set=set_obj, bit_id="no-beats", line_start=1, line_end=1)

    resp = client.get("/api/killtony/bits/")
    assert resp.json() == []

import pytest

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def search_data(db):
    comedian = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", set_count=1)
    Comedian.objects.create(name="Casey No Sets", slug="casey-no-sets")
    video = Video.objects.create(video_id="abc123xyz01", number=700, title="Kill Tony #700", url="https://example.com/kt-700", set_count=1)
    set_obj = Set.objects.create(video=video, comedian=comedian, set_number=1, start_seconds=0, bit_count=1)
    bit = Bit.objects.create(set=set_obj, bit_id="b1", summary="A rocket joke", line_start=1, line_end=2)
    beat = Beat.objects.create(bit=bit, beat_id="beat-1", line_start=1, line_end=3, premise="A clean premise", joke_type="misdirect")
    Line.objects.bulk_create([
        Line(set=set_obj, line_number=1, label="setup", text="hello there", start_seconds=0),
        Line(set=set_obj, line_number=2, label="fluff", text="this fluff line should stay ignored", start_seconds=1),
        Line(set=set_obj, line_number=3, label="punchline", text="this line should not make the comedian searchable globally", start_seconds=2),
    ])
    return {"comedian": comedian, "video": video, "set": set_obj, "beat": beat}


def test_global_search_does_not_match_comedians_from_transcript_text(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "hello"})
    assert resp.status_code == 200
    assert resp.json()["comedians"] == []
    assert resp.json()["beats"][0]["title"] == "hello there"
    assert resp.json()["beats"][0]["matched_line_label"] == "setup"


def test_global_comedian_matches_comedian_endpoint(client, search_data):
    global_resp = client.get("/api/killtony/search/", {"q": "casey"})
    comedian_resp = client.get("/api/killtony/comedians/", {"q": "casey"})

    assert global_resp.status_code == 200
    assert comedian_resp.status_code == 200
    global_names = [item["title"] for item in global_resp.json()["comedians"]]
    comedian_names = [item["name"] for item in comedian_resp.json()]
    assert global_names == comedian_names == ["Casey Rocket"]


def test_comedian_endpoint_excludes_comedians_without_sets(client, search_data):
    resp = client.get("/api/killtony/comedians/", {"q": "casey"})
    assert resp.status_code == 200
    assert [item["name"] for item in resp.json()] == ["Casey Rocket"]


def test_beat_search_ignores_fluff_lines(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "ignored"})
    assert resp.status_code == 200
    assert resp.json()["beats"] == []


def test_beat_endpoint_returns_matched_line(client, search_data):
    resp = client.get("/api/killtony/jokes/", {"q": "hello"})
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload) == 1
    assert payload[0]["id"] == search_data["beat"].id
    assert payload[0]["matched_line"] == "hello there"
    assert payload[0]["matched_line_label"] == "setup"

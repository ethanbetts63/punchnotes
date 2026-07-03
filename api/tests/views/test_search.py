import pytest

from pipeline.models import Beat, Bit, Comedian, Line, Set, Video
from pipeline.utils.beat_search import build_beat_search_text


pytestmark = pytest.mark.django_db


@pytest.fixture
def search_data(db):
    comedian = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", set_count=1)
    Comedian.objects.create(name="Casey No Sets", slug="casey-no-sets")
    video = Video.objects.create(video_id="abc123xyz01", number=700, title="Kill Tony #700", url="https://example.com/kt-700", set_count=1)
    set_obj = Set.objects.create(video=video, comedian=comedian, set_number=1, start_seconds=0, bit_count=1)
    bit = Bit.objects.create(set=set_obj, bit_id="b1", line_start=1, line_end=2)
    lines_data = [
        {"line_number": 1, "label": "setup", "text": "hello there"},
        {"line_number": 2, "label": "fluff", "text": "this fluff line should stay ignored"},
        {"line_number": 3, "label": "punchline", "text": "this line should not make the comedian searchable globally"},
    ]
    beat = Beat.objects.create(
        bit=bit, beat_id="beat-1", line_start=1, line_end=3, premise="A clean premise", joke_type="misdirect",
        search_text=build_beat_search_text(lines_data, {1, 2, 3}),
    )
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


# --- NavSearchView ---

def test_nav_search_empty_query_returns_empty_structure(client):
    resp = client.get("/api/killtony/search/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == ""
    assert "top_result" not in data
    assert data["comedians"] == []
    assert data["episodes"] == []
    assert data["beats"] == []


def test_nav_search_returns_all_buckets(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "casey"})
    assert resp.status_code == 200
    data = resp.json()
    assert "comedians" in data
    assert "episodes" in data
    assert "sets" in data
    assert "beats" in data


def test_nav_search_episode_links_use_stable_slug(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "700"})
    data = resp.json()
    assert data["episodes"][0]["href"] == "/killtony/episodes/kill-tony-700--abc123xyz01"


def test_nav_search_set_links_use_stable_slug(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "casey"})
    data = resp.json()
    assert data["sets"][0]["href"] == "/killtony/sets/abc123xyz01-set01-casey-rocket"


def test_nav_search_beat_links_use_stable_set_slug(client, search_data):
    resp = client.get("/api/killtony/search/", {"q": "hello"})
    data = resp.json()
    assert data["beats"][0]["href"] == "/killtony/sets/abc123xyz01-set01-casey-rocket?bit=001&beat=001"

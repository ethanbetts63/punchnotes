import pytest

from pipeline.models import Comedian, Set, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def comedian_data(db):
    video = Video.objects.create(video_id="aaa0000001", number=700, title="KT #700", url="https://example.com/700")
    c1 = Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", attributes=["man", "regular"], set_count=1, has_large_joke_book=True)
    c2 = Comedian.objects.create(name="Dana Blue", slug="dana-blue", attributes=["woman"], set_count=1)
    no_set = Comedian.objects.create(name="Nobody", slug="nobody")
    Set.objects.create(video=video, comedian=c1, start_seconds=0, attributes=["large_joke_book"])
    Set.objects.create(video=video, comedian=c2, start_seconds=100)
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
    sets = resp.json()["sets"]
    assert len(sets) == 1
    assert sets[0]["slug"] == "aaa0000001-0-casey-rocket"
    assert sets[0]["start_seconds"] == 0
    assert sets[0]["bit_count"] == 0


def test_comedian_detail_404_on_missing(client):
    resp = client.get("/api/killtony/comedians/nobody-here/")
    assert resp.status_code == 404


def test_comedian_detail_samples_jokes_without_fluff(client, full_set):
    resp = client.get("/api/killtony/comedians/casey-rocket/")
    jokes = resp.json()["sets"][0]["sample_jokes"]
    assert jokes == [{
        "beat_id": "beat-1",
        "joke_type": "reframe",
        "lines": [
            {"label": "setup", "text": "I used to be an astronaut."},
            {"label": "punchline", "text": "I was a rocket scientist though."},
        ],
    }]


def test_comedian_detail_sample_is_capped_and_stable(client, full_set):
    from pipeline.models import Beat, Line

    for n in range(4, 10):
        Line.objects.create(set=full_set["set"], line_number=n, label="punchline", text=f"Joke {n}", start_seconds=60 + n)
        Beat.objects.create(bit=full_set["bit"], beat_id=f"beat-{n}", line_start=n, line_end=n)

    first = client.get("/api/killtony/comedians/casey-rocket/").json()["sets"][0]["sample_jokes"]
    second = client.get("/api/killtony/comedians/casey-rocket/").json()["sets"][0]["sample_jokes"]
    assert len(first) == 2
    assert first == second


def test_comedian_detail_counts_joke_types(client, full_set):
    from pipeline.models import Beat

    Beat.objects.create(bit=full_set["bit"], beat_id="beat-2", line_start=3, line_end=3, joke_type="misdirect")
    Beat.objects.create(bit=full_set["bit"], beat_id="beat-3", line_start=3, line_end=3, joke_type="misdirect")
    Beat.objects.create(bit=full_set["bit"], beat_id="beat-4", line_start=3, line_end=3)

    counts = client.get("/api/killtony/comedians/casey-rocket/").json()["joke_type_counts"]
    assert list(counts.items()) == [("misdirect", 2), ("reframe", 1)]


def test_joke_excerpt_keeps_the_punchline_of_a_long_joke():
    from api.serializers.comedian import joke_excerpt

    lines = [{"label": "setup", "text": f"Setup {n}"} for n in range(1, 8)]
    lines += [{"label": "punchline", "text": "Punch"}]
    lines += [{"label": "tag", "text": f"Tag {n}"} for n in range(1, 5)]
    assert [line["text"] for line in joke_excerpt(lines)] == [
        "Setup 5", "Setup 6", "Setup 7", "Punch", "Tag 1", "Tag 2",
    ]


def test_comedian_detail_queries_do_not_grow_with_sets(client, full_set, django_assert_max_num_queries):
    from pipeline.models import Beat, Bit, Line, Set, Video

    for n in range(5):
        video = Video.objects.create(video_id=f"vid{n:08d}", number=600 + n, title=f"KT #{600 + n}", url=f"https://example.com/{n}")
        set_obj = Set.objects.create(video=video, comedian=full_set["comedian"], start_seconds=0)
        bit = Bit.objects.create(set=set_obj, bit_id="b1", line_start=1, line_end=1)
        Beat.objects.create(bit=bit, beat_id="beat-1", line_start=1, line_end=1, joke_type="misdirect")
        Line.objects.create(set=set_obj, line_number=1, label="punchline", text="Joke", start_seconds=0)

    with django_assert_max_num_queries(6):
        resp = client.get("/api/killtony/comedians/casey-rocket/")
    assert len(resp.json()["sets"]) == 6

import pytest
from django.test import override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.models import Comedian


pytestmark = pytest.mark.django_db


class DefaultPermissionProbeView(APIView):
    def get(self, request):
        return Response({"status": "ok"})


urlpatterns = [
    path("probe/", DefaultPermissionProbeView.as_view()),
]


@override_settings(ROOT_URLCONF=__name__)
def test_drf_views_are_private_by_default(client):
    resp = client.get("/probe/")
    assert resp.status_code == 403


def test_catalogue_endpoint_is_explicitly_public(client):
    Comedian.objects.create(name="Casey Rocket", slug="casey-rocket", set_count=1)

    resp = client.get("/api/killtony/comedians/")

    assert resp.status_code == 200


def test_api_responses_are_not_cacheable(client):
    resp = client.get("/api/killtony/search/")

    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "no-store"


def test_pipeline_endpoint_rejects_wrong_bearer_token(client, settings):
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {settings.PIPELINE_API_KEY}-wrong"

    resp = client.get("/api/pipeline/videos-to-scrape/")

    assert resp.status_code == 403


def test_plagiarism_rejects_non_string_text(client):
    resp = client.post(
        "/api/killtony/plagiarism/",
        data={"text": ["not", "a", "string"]},
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert resp.json()["error"] == "text must be a string"


def test_plagiarism_rejects_overlong_text(client):
    resp = client.post(
        "/api/killtony/plagiarism/",
        data={"text": "x" * 2001},
        content_type="application/json",
    )

    assert resp.status_code == 400
    assert "characters or fewer" in resp.json()["error"]

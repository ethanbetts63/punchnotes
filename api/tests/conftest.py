import pytest
from django.conf import settings


@pytest.fixture
def api_client():
    from django.test import Client
    client = Client()
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {settings.PIPELINE_API_KEY}"
    return client

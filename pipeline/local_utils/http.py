import requests
from django.conf import settings


def pipeline_session() -> requests.Session:
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {settings.PIPELINE_API_KEY}"
    return s


def server_url(path: str) -> str:
    base = settings.SERVER_BASE_URL.rstrip("/")
    return f"{base}{path}"

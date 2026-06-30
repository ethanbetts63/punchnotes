import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DATA_DIR = BASE_DIR / "pipeline" / "data"
PIPELINE_PRIVATE_DATA_DIR = BASE_DIR / "pipeline" / "data_private"

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ["DEBUG"] == "True"

_api_host = urlparse(os.environ["SERVER_BASE_URL"]).hostname
ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + ([_api_host] if _api_host else [])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "pipeline",
    "api",
]

LOCAL_FRONTEND_URL = os.environ["LOCAL_FRONTEND_URL"]
PRODUCTION_FRONTEND_URL = os.environ.get("PRODUCTION_FRONTEND_URL")

CORS_ALLOWED_ORIGINS = [LOCAL_FRONTEND_URL] + ([PRODUCTION_FRONTEND_URL])

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PIPELINE_API_KEY = os.environ["PIPELINE_API_KEY"]
SERVER_BASE_URL = os.environ["SERVER_BASE_URL"]
LOCAL_SERVER_URL = os.environ["LOCAL_SERVER_URL"]
HF_API_KEY = os.environ["punchnotes_embedding_token"]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

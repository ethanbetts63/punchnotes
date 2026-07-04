import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_DIR = Path(__file__).resolve().parent.parent
PIPELINE_DATA_DIR = BASE_DIR / "pipeline" / "data"
PIPELINE_PRIVATE_DATA_DIR = BASE_DIR / "pipeline" / "data_private"


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = env_bool("DEBUG")

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

FRONTEND_ORIGINS = [origin for origin in [LOCAL_FRONTEND_URL, PRODUCTION_FRONTEND_URL] if origin]
CORS_ALLOWED_ORIGINS = FRONTEND_ORIGINS
CSRF_TRUSTED_ORIGINS = FRONTEND_ORIGINS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "config.middleware.NoCacheApiMiddleware",
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
VERCEL_BUILD_API_KEY = os.environ.get("VERCEL_BUILD_API_KEY", "")
SERVER_BASE_URL = os.environ["SERVER_BASE_URL"]
LOCAL_SERVER_URL = os.environ["LOCAL_SERVER_URL"]
HF_API_KEY = os.environ["punchnotes_embedding_token"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "api.throttling.BuildAwareAnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "api.throttling.BuildAwareScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.environ.get("DRF_ANON_THROTTLE_RATE", "300/hour"),
        "user": os.environ.get("DRF_USER_THROTTLE_RATE", "2000/hour"),
        "catalogue": os.environ.get("DRF_CATALOGUE_THROTTLE_RATE", "120/min"),
        "search": os.environ.get("DRF_SEARCH_THROTTLE_RATE", "60/min"),
        "plagiarism": os.environ.get("DRF_PLAGIARISM_THROTTLE_RATE", "10/hour"),
        "pipeline": os.environ.get("DRF_PIPELINE_THROTTLE_RATE", "120/min"),
    },
}

SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", not DEBUG)
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https")
    if env_bool("TRUST_X_FORWARDED_PROTO", not DEBUG)
    else None
)
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", not DEBUG)
SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

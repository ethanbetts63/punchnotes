from django.conf import settings
from rest_framework import serializers


def absolute_media_url(value, request=None):
    """Turn a stored MEDIA_ROOT-relative path into an absolute URL at read time.

    Mirrors allbikes' serializer `build_absolute_uri` pattern: the host is taken
    from the incoming request, so the same DB value works across local/prod and
    survives a domain change. Falls back to SERVER_BASE_URL when no request is in
    context, and passes through values that are already absolute (legacy rows).
    """
    if not value:
        return None
    if value.startswith(("http://", "https://")):
        return value
    path = f"{settings.MEDIA_URL}{value.lstrip('/')}"
    if request is not None:
        return request.build_absolute_uri(path)
    return f"{settings.SERVER_BASE_URL.rstrip('/')}{path}"


class AbsoluteMediaUrlField(serializers.Field):
    """Read-only field that renders a MEDIA_ROOT-relative path as an absolute URL."""

    def __init__(self, **kwargs):
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def to_representation(self, value):
        return absolute_media_url(value, self.context.get("request"))

from secrets import compare_digest

from django.conf import settings
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle


BUILD_KEY_HEADER = "HTTP_X_PUNCHNOTES_BUILD_KEY"


def has_valid_build_key(request) -> bool:
    expected = getattr(settings, "VERCEL_BUILD_API_KEY", "")
    supplied = request.META.get(BUILD_KEY_HEADER, "")
    return bool(expected) and bool(supplied) and compare_digest(supplied, expected)


class BuildAwareAnonRateThrottle(AnonRateThrottle):
    def allow_request(self, request, view):
        if has_valid_build_key(request):
            return True
        return super().allow_request(request, view)


class BuildAwareScopedRateThrottle(ScopedRateThrottle):
    def allow_request(self, request, view):
        if has_valid_build_key(request):
            return True
        return super().allow_request(request, view)

from secrets import compare_digest

from django.conf import settings
from rest_framework.permissions import BasePermission


class PipelineKeyPermission(BasePermission):
    def has_permission(self, request, view):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return False
        token = auth[7:]
        expected = getattr(settings, "PIPELINE_API_KEY", None)
        return bool(expected) and compare_digest(token, expected)

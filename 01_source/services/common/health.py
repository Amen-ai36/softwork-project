"""Operational endpoints shared by all independently deployed services."""

import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def live(_request):
    return JsonResponse({"status": "ok", "service": settings.SERVICE_NAME})


def ready(_request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {"status": "unavailable", "service": settings.SERVICE_NAME}, status=503
        )
    return JsonResponse({"status": "ready", "service": settings.SERVICE_NAME})


def version(_request):
    return JsonResponse(
        {
            "service": settings.SERVICE_NAME,
            "version": os.environ.get("APP_VERSION", "dev"),
        }
    )

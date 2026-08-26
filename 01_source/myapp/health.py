"""Operational endpoints used by containers and deployment automation."""

import os

from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live(request):
    return JsonResponse({"status": "ok", "service": "food-master"})


@require_GET
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {"status": "unavailable", "service": "food-master"}, status=503
        )
    return JsonResponse({"status": "ready", "service": "food-master"})


@require_GET
def version(request):
    return JsonResponse(
        {
            "service": "food-master",
            "version": os.environ.get("APP_VERSION", "dev"),
        }
    )

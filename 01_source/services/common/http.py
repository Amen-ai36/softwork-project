"""HTTP helpers that keep service responses and validation predictable."""

import json

from django.http import JsonResponse


def body(request):
    if not request.body:
        return {}
    try:
        value = json.loads(request.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("request body must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("request body must be a JSON object")
    return value


def error(message, status=400, **details):
    payload = {"error": message}
    payload.update(details)
    return JsonResponse(payload, status=status)


def method_not_allowed(*allowed):
    response = error("method not allowed", 405, allowed=list(allowed))
    response["Allow"] = ", ".join(allowed)
    return response


def values(model, fields):
    return {field: getattr(model, field) for field in fields}

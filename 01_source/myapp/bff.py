"""BFF aggregation layer that fans out to the three business services.

The Backend-for-Frontend issues concurrent HTTP calls to user/trade/lifestyle
services and merges the results instead of reading the old monolith database.
Each upstream call degrades independently: a failing service returns an error
block without failing the whole aggregate response.
"""

import os
from concurrent.futures import ThreadPoolExecutor

import requests
from django.http import JsonResponse

from services.common.auth import TokenError, decode_token

DEFAULT_PORTS = {"user": 8001, "trade": 8002, "lifestyle": 8003}
TIMEOUT = 2.0


def _service_url(service):
    key = f"{service.upper()}_SERVICE_URL"
    return os.environ.get(key, f"http://127.0.0.1:{DEFAULT_PORTS[service]}")


def _get(service, path, token=None):
    url = f"{_service_url(service)}{path}"
    headers = {
        "X-Internal-Token": os.environ.get(
            "INTERNAL_SERVICE_TOKEN", "dev-internal-token"
        )
    }
    if token:
        headers["Authorization"] = token
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        if response.status_code == 200:
            return {"ok": True, "data": response.json()}
        return {"ok": False, "error": f"upstream {response.status_code}"}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": str(exc)}


def _fanout(calls):
    with ThreadPoolExecutor(max_workers=len(calls)) as executor:
        futures = [executor.submit(_get, *call) for call in calls]
        return [future.result() for future in futures]


def _block(result):
    return result["data"] if result["ok"] else {"error": result["error"]}


def _errors(results):
    return [result["error"] for result in results if not result["ok"]]


def health_aggregate(request):
    calls = [
        ("user", "/health/live"),
        ("trade", "/health/live"),
        ("lifestyle", "/health/live"),
    ]
    results = _fanout(calls)
    services = {}
    for (name, _path), result in zip(calls, results):
        services[name] = (
            result["data"]
            if result["ok"]
            else {"status": "unavailable", "error": result["error"]}
        )
    return JsonResponse({"services": services})


def catalog_aggregate(request):
    calls = [
        ("trade", "/foods"),
        ("lifestyle", "/hotels"),
        ("lifestyle", "/plays"),
    ]
    results = _fanout(calls)
    foods = _block(results[0])
    hotels = _block(results[1])
    plays = _block(results[2])
    return JsonResponse(
        {
            "foods": foods.get("foods", []) if isinstance(foods, dict) else [],
            "hotels": hotels.get("hotels", []) if isinstance(hotels, dict) else [],
            "plays": plays.get("plays", []) if isinstance(plays, dict) else [],
            "errors": _errors(results),
        }
    )


def space_aggregate(request):
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return JsonResponse({"error": "missing bearer token"}, status=401)
    try:
        claims = decode_token(authorization[7:].strip())
    except TokenError as exc:
        return JsonResponse({"error": str(exc)}, status=401)
    user_id = int(claims["user_id"])
    calls = [
        ("user", f"/users/{user_id}", authorization),
        ("trade", "/cart", authorization),
        ("lifestyle", "/blogs", None),
    ]
    results = _fanout(calls)
    return JsonResponse(
        {
            "profile": _block(results[0]),
            "cart": _block(results[1]),
            "blogs": _block(results[2]),
            "errors": _errors(results),
        }
    )

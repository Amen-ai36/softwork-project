"""Minimal cross-service HTTP client with graceful degradation.

Services call each other over HTTP using an internal token. Every call is
best-effort: on any network error, timeout, or non-200 response the caller
receives ``None``/``{}`` and must fall back to a placeholder instead of
failing the request.
"""

import json
import os
import urllib.error
import urllib.request

DEFAULT_TIMEOUT = 1.0
DEFAULT_PORTS = {"user": 8001, "trade": 8002, "lifestyle": 8003}


def _service_url(service, default_port):
    key = f"{service.upper()}_SERVICE_URL"
    return os.environ.get(key, f"http://127.0.0.1:{default_port}")


def _internal_token():
    return os.environ.get("INTERNAL_SERVICE_TOKEN", "dev-internal-token")


def get_json(url, timeout=DEFAULT_TIMEOUT):
    """GET ``url`` and parse a JSON object; return ``None`` on any failure."""
    request = urllib.request.Request(
        url, headers={"X-Internal-Token": _internal_token()}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return None
            return json.loads(response.read().decode("utf-8"))
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        OSError,
        ValueError,
    ):
        return None


def resolve_usernames(user_ids):
    """Batch-resolve user IDs to usernames via user-service ``/internal/users``.

    Returns ``{user_id: username}``; empty dict on failure so callers can fall
    back to an anonymous placeholder.
    """
    ids = sorted({int(value) for value in user_ids if value})
    if not ids:
        return {}
    base = _service_url("user", DEFAULT_PORTS["user"])
    url = f"{base}/internal/users?ids={','.join(map(str, ids))}"
    payload = get_json(url)
    if not payload or not isinstance(payload.get("users"), list):
        return {}
    return {int(user["id"]): user["username"] for user in payload["users"]}

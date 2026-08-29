"""Minimal HS256 JWT implementation used consistently by all services."""

import base64
import hashlib
import hmac
import json
import os
import time
from functools import wraps

from django.http import JsonResponse


class TokenError(ValueError):
    pass


def _b64_encode(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64_decode(value):
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _secret():
    return os.environ.get("JWT_SECRET", os.environ.get("DJANGO_SECRET_KEY", "dev-jwt"))


def issue_token(user_id, usertype, lifetime=3600):
    now = int(time.time())
    header = _b64_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64_encode(
        json.dumps(
            {
                "sub": str(user_id),
                "user_id": int(user_id),
                "usertype": int(usertype),
                "iat": now,
                "exp": now + lifetime,
            },
            separators=(",", ":"),
        ).encode()
    )
    signing_input = f"{header}.{payload}".encode("ascii")
    signature = hmac.new(_secret().encode(), signing_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64_encode(signature)}"


def decode_token(token):
    try:
        header, payload, signature = token.split(".")
        signing_input = f"{header}.{payload}".encode("ascii")
        expected = hmac.new(_secret().encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64_decode(signature)):
            raise TokenError("invalid signature")
        claims = json.loads(_b64_decode(payload))
        if int(claims.get("exp", 0)) <= int(time.time()):
            raise TokenError("token expired")
        return claims
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        if isinstance(exc, TokenError):
            raise
        raise TokenError("invalid token") from exc


def request_claims(request):
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise TokenError("missing bearer token")
    return decode_token(authorization[7:].strip())


def require_auth(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            try:
                claims = request_claims(request)
            except TokenError as exc:
                return JsonResponse({"error": str(exc)}, status=401)
            if roles and int(claims.get("usertype", -1)) not in roles:
                return JsonResponse({"error": "forbidden"}, status=403)
            request.claims = claims
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def internal_or_authenticated(request):
    internal = request.headers.get("X-Internal-Token", "")
    expected = os.environ.get("INTERNAL_SERVICE_TOKEN", "dev-internal-token")
    if internal and hmac.compare_digest(internal, expected):
        return {"internal": True, "usertype": 3}
    return request_claims(request)

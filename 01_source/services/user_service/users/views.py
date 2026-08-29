import re

from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.http import JsonResponse

from services.common.auth import (
    TokenError,
    internal_or_authenticated,
    issue_token,
    require_auth,
)
from services.common.http import body, error, method_not_allowed
from services.user_service.users.models import User

PUBLIC_FIELDS = ("id", "username", "phone", "word", "usertype", "is_active")
PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,16}$")


def serialize_user(user):
    return {field: getattr(user, field) for field in PUBLIC_FIELDS}


def register(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
        username = str(data.get("username", "")).strip()
        password = str(data.get("password", ""))
        phone = str(data.get("phone", "")).strip()
        usertype = int(data.get("usertype", 0))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not username or len(username) > 20:
        return error("username must contain 1 to 20 characters")
    if not PASSWORD_RE.match(password):
        return error("password must be 8-16 characters with letters and digits")
    if not (phone.isdigit() and len(phone) == 11):
        return error("phone must contain exactly 11 digits")
    if usertype not in (0, 1, 2):
        return error("public registration only supports user, rider, or merchant")
    try:
        user = User.objects.create(
            username=username,
            password=make_password(password),
            phone=phone,
            usertype=usertype,
        )
    except IntegrityError:
        return error("username already exists", 409)
    return JsonResponse({"user": serialize_user(user)}, status=201)


def login(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    user = User.objects.filter(username=str(data.get("username", "")).strip()).first()
    if not user or not check_password(str(data.get("password", "")), user.password):
        return error("invalid credentials", 401)
    if not user.is_active:
        return error("account disabled", 403)
    return JsonResponse(
        {
            "access_token": issue_token(user.id, user.usertype),
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": serialize_user(user),
        }
    )


@require_auth()
def logout(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    return JsonResponse({"status": "logged_out"})


@require_auth()
def user_detail(request, user_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    if (
        int(request.claims["user_id"]) != user_id
        and int(request.claims["usertype"]) != 3
    ):
        return error("forbidden", 403)
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error("user not found", 404)
    return JsonResponse({"user": serialize_user(user)})


@require_auth()
def user_profile(request, user_id):
    if request.method != "PATCH":
        return method_not_allowed("PATCH")
    if (
        int(request.claims["user_id"]) != user_id
        and int(request.claims["usertype"]) != 3
    ):
        return error("forbidden", 403)
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error("user not found", 404)
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    if "phone" in data:
        phone = str(data["phone"])
        if not (phone.isdigit() and len(phone) == 11):
            return error("phone must contain exactly 11 digits")
        user.phone = phone
    if "word" in data:
        user.word = str(data["word"])[:50]
    user.save(update_fields=["phone", "word", "updated_at"])
    return JsonResponse({"user": serialize_user(user)})


@require_auth(3)
def user_status(request, user_id):
    if request.method != "PATCH":
        return method_not_allowed("PATCH")
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error("user not found", 404)
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    if not isinstance(data.get("is_active"), bool):
        return error("is_active must be a boolean")
    user.is_active = data["is_active"]
    user.save(update_fields=["is_active", "updated_at"])
    return JsonResponse({"user": serialize_user(user)})


@require_auth(3)
def user_role(request, user_id):
    if request.method != "PATCH":
        return method_not_allowed("PATCH")
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error("user not found", 404)
    try:
        data = body(request)
        usertype = int(data.get("usertype"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if usertype not in (0, 1, 2, 3):
        return error("unsupported user role")
    user.usertype = usertype
    user.save(update_fields=["usertype", "updated_at"])
    return JsonResponse({"user": serialize_user(user)})


def internal_users(request):
    if request.method != "GET":
        return method_not_allowed("GET")
    try:
        internal_or_authenticated(request)
        ids = [int(value) for value in request.GET.get("ids", "").split(",") if value]
    except (TokenError, ValueError) as exc:
        return error(str(exc), 401)
    users = User.objects.filter(id__in=ids[:100], is_active=True)
    return JsonResponse({"users": [serialize_user(user) for user in users]})

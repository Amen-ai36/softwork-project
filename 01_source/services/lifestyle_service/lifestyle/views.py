from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime

from services.common.auth import require_auth
from services.common.http import body, error, method_not_allowed
from services.lifestyle_service.lifestyle.models import (
    Blog,
    Comment,
    Hotel,
    HotelOrder,
    Play,
    PlayOrder,
)

HOTEL_FIELDS = (
    "id",
    "name",
    "addr",
    "price_clock",
    "price_day",
    "price_double_clock",
    "price_double_day",
    "price_special",
    "image",
    "rating",
    "ratenum",
    "orders",
    "inf",
    "merchant_id",
)
PLAY_FIELDS = (
    "id",
    "name",
    "addr",
    "price",
    "start_time",
    "open_time",
    "image",
    "rating",
    "ratenum",
    "orders",
    "inf",
    "merchant_id",
)
HOTEL_ORDER_FIELDS = (
    "id",
    "user_id",
    "hotel_id",
    "room_type",
    "duration",
    "checkin_time",
    "time",
    "cost",
    "comment",
    "score",
    "pos",
)
PLAY_ORDER_FIELDS = (
    "id",
    "user_id",
    "play_id",
    "num",
    "visit_time",
    "time",
    "cost",
    "comment",
    "score",
    "pos",
)


def serialize(instance, fields):
    return {field: getattr(instance, field) for field in fields}


def positive_int(value, name):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed < 1:
        raise ValueError(f"{name} must be positive")
    return parsed


def requested_datetime(value, name):
    parsed = parse_datetime(str(value or ""))
    if parsed is None:
        raise ValueError(f"{name} must be an ISO-8601 datetime")
    return parsed


def hotels(request):
    if request.method == "GET":
        keyword = request.GET.get("q", "").strip()
        queryset = Hotel.objects.all()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(addr__icontains=keyword)
                | Q(inf__icontains=keyword)
            )
        return JsonResponse(
            {"hotels": [serialize(hotel, HOTEL_FIELDS) for hotel in queryset]}
        )
    if request.method != "POST":
        return method_not_allowed("GET", "POST")
    return create_hotel(request)


@require_auth(2)
def create_hotel(request):
    try:
        data = body(request)
        name = str(data.get("name", "")).strip()
        addr = str(data.get("addr", "")).strip()
        price_day = float(data.get("price_day"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not name or not addr or price_day <= 0:
        return error("name, address, and a positive daily price are required")
    hotel = Hotel.objects.create(
        name=name,
        addr=addr,
        price_clock=data.get("price_clock"),
        price_day=price_day,
        price_double_clock=data.get("price_double_clock"),
        price_double_day=data.get("price_double_day"),
        price_special=data.get("price_special"),
        image=str(data.get("image", "")),
        inf=str(data.get("inf", "")),
        merchant_id=int(request.claims["user_id"]),
    )
    return JsonResponse({"hotel": serialize(hotel, HOTEL_FIELDS)}, status=201)


def hotel_detail(request, hotel_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    hotel = Hotel.objects.filter(id=hotel_id).first()
    if not hotel:
        return error("hotel not found", 404)
    return JsonResponse({"hotel": serialize(hotel, HOTEL_FIELDS)})


@require_auth(0)
def hotel_orders(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
        hotel = Hotel.objects.filter(id=int(data.get("hotel_id"))).first()
        duration = positive_int(data.get("duration"), "duration")
        checkin_time = requested_datetime(data.get("checkin_time"), "checkin_time")
        room_type = str(data.get("room_type", "single_day"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not hotel:
        return error("hotel not found", 404)
    price_map = {
        "single_clock": hotel.price_clock,
        "single_day": hotel.price_day,
        "double_clock": hotel.price_double_clock,
        "double_day": hotel.price_double_day,
        "special_day": hotel.price_special,
    }
    price = price_map.get(room_type)
    if price is None:
        return error("unsupported or unavailable room type")
    with transaction.atomic():
        order = HotelOrder.objects.create(
            user_id=int(request.claims["user_id"]),
            hotel=hotel,
            room_type=room_type,
            duration=duration,
            checkin_time=checkin_time,
            cost=round(float(price) * duration, 2),
        )
        hotel.orders += 1
        hotel.save(update_fields=["orders"])
    return JsonResponse({"order": serialize(order, HOTEL_ORDER_FIELDS)}, status=201)


@require_auth()
def hotel_order_detail(request, order_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    order = HotelOrder.objects.select_related("hotel").filter(id=order_id).first()
    if not order:
        return error("hotel order not found", 404)
    user_id = int(request.claims["user_id"])
    role = int(request.claims["usertype"])
    if user_id != order.user_id and not (
        role == 3 or (role == 2 and order.hotel.merchant_id == user_id)
    ):
        return error("forbidden", 403)
    return JsonResponse({"order": serialize(order, HOTEL_ORDER_FIELDS)})


@require_auth(0)
def hotel_order_comment(request, order_id):
    if request.method != "POST":
        return method_not_allowed("POST")
    order = (
        HotelOrder.objects.select_related("hotel")
        .filter(id=order_id, user_id=request.claims["user_id"])
        .first()
    )
    if not order:
        return error("hotel order not found", 404)
    try:
        data = body(request)
        score = float(data.get("score"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not 0 <= score <= 5:
        return error("score must be between 0 and 5")
    order.comment = str(data.get("comment", ""))[:200]
    order.score = round(score, 1)
    order.pos = 5
    order.save(update_fields=["comment", "score", "pos"])
    refresh_hotel_rating(order.hotel)
    return JsonResponse({"order": serialize(order, HOTEL_ORDER_FIELDS)})


def refresh_hotel_rating(hotel):
    scores = [
        float(value)
        for value in hotel.bookings.filter(score__gt=0).values_list("score", flat=True)
    ]
    hotel.rating = round(sum(scores) / len(scores), 1) if scores else 0
    hotel.ratenum = len(scores)
    hotel.save(update_fields=["rating", "ratenum"])


def plays(request):
    if request.method == "GET":
        keyword = request.GET.get("q", "").strip()
        queryset = Play.objects.all()
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(addr__icontains=keyword)
                | Q(inf__icontains=keyword)
            )
        return JsonResponse(
            {"plays": [serialize(play, PLAY_FIELDS) for play in queryset]}
        )
    if request.method != "POST":
        return method_not_allowed("GET", "POST")
    return create_play(request)


@require_auth(2)
def create_play(request):
    try:
        data = body(request)
        name = str(data.get("name", "")).strip()
        addr = str(data.get("addr", "")).strip()
        price = float(data.get("price"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not name or not addr or price <= 0:
        return error("name, address, and a positive price are required")
    play = Play.objects.create(
        name=name,
        addr=addr,
        price=price,
        start_time=str(data.get("start_time", "09:00")),
        open_time=str(data.get("open_time", "24h")),
        image=str(data.get("image", "")),
        inf=str(data.get("inf", "")),
        merchant_id=int(request.claims["user_id"]),
    )
    return JsonResponse({"play": serialize(play, PLAY_FIELDS)}, status=201)


def play_detail(request, play_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    play = Play.objects.filter(id=play_id).first()
    if not play:
        return error("play not found", 404)
    return JsonResponse({"play": serialize(play, PLAY_FIELDS)})


@require_auth(0)
def play_orders(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
        play = Play.objects.filter(id=int(data.get("play_id"))).first()
        num = positive_int(data.get("num", 1), "num")
        visit_time = requested_datetime(data.get("visit_time"), "visit_time")
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not play:
        return error("play not found", 404)
    with transaction.atomic():
        order = PlayOrder.objects.create(
            user_id=int(request.claims["user_id"]),
            play=play,
            num=num,
            visit_time=visit_time,
            cost=round(play.price * num, 2),
        )
        play.orders += 1
        play.save(update_fields=["orders"])
    return JsonResponse({"order": serialize(order, PLAY_ORDER_FIELDS)}, status=201)


@require_auth()
def play_order_detail(request, order_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    order = PlayOrder.objects.select_related("play").filter(id=order_id).first()
    if not order:
        return error("play order not found", 404)
    user_id = int(request.claims["user_id"])
    role = int(request.claims["usertype"])
    if user_id != order.user_id and not (
        role == 3 or (role == 2 and order.play.merchant_id == user_id)
    ):
        return error("forbidden", 403)
    return JsonResponse({"order": serialize(order, PLAY_ORDER_FIELDS)})


@require_auth(0)
def play_order_comment(request, order_id):
    if request.method != "POST":
        return method_not_allowed("POST")
    order = (
        PlayOrder.objects.select_related("play")
        .filter(id=order_id, user_id=request.claims["user_id"])
        .first()
    )
    if not order:
        return error("play order not found", 404)
    try:
        data = body(request)
        score = float(data.get("score"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not 0 <= score <= 5:
        return error("score must be between 0 and 5")
    order.comment = str(data.get("comment", ""))[:200]
    order.score = round(score, 1)
    order.pos = 5
    order.save(update_fields=["comment", "score", "pos"])
    scores = [
        float(value)
        for value in order.play.bookings.filter(score__gt=0).values_list(
            "score", flat=True
        )
    ]
    order.play.rating = round(sum(scores) / len(scores), 1) if scores else 0
    order.play.ratenum = len(scores)
    order.play.save(update_fields=["rating", "ratenum"])
    return JsonResponse({"order": serialize(order, PLAY_ORDER_FIELDS)})


def blogs(request):
    if request.method == "GET":
        queryset = Blog.objects.filter(is_deleted=False).order_by("-created_at")
        return JsonResponse(
            {
                "blogs": [
                    {
                        "id": blog.id,
                        "title": blog.title,
                        "content": blog.content,
                        "author_id": blog.author_id,
                        "created_at": blog.created_at,
                    }
                    for blog in queryset
                ]
            }
        )
    if request.method != "POST":
        return method_not_allowed("GET", "POST")
    return create_blog(request)


@require_auth(0, 1, 2, 3)
def create_blog(request):
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    if not title or not content:
        return error("title and content are required")
    blog = Blog.objects.create(
        title=title[:40], content=content, author_id=int(request.claims["user_id"])
    )
    return JsonResponse({"blog_id": blog.id}, status=201)


def blog_detail(request, blog_id):
    blog = Blog.objects.filter(id=blog_id, is_deleted=False).first()
    if not blog:
        return error("blog not found", 404)
    if request.method == "GET":
        comments = blog.comments.filter(is_deleted=False).order_by("created_at")
        return JsonResponse(
            {
                "blog": {
                    "id": blog.id,
                    "title": blog.title,
                    "content": blog.content,
                    "author_id": blog.author_id,
                    "created_at": blog.created_at,
                },
                "comments": [
                    {
                        "id": comment.id,
                        "user_id": comment.user_id,
                        "content": comment.content,
                        "created_at": comment.created_at,
                    }
                    for comment in comments
                ],
            }
        )
    if request.method != "DELETE":
        return method_not_allowed("GET", "DELETE")
    return delete_blog(request, blog)


@require_auth()
def delete_blog(request, blog):
    if int(request.claims["usertype"]) != 3 and blog.author_id != int(
        request.claims["user_id"]
    ):
        return error("forbidden", 403)
    blog.is_deleted = True
    blog.save(update_fields=["is_deleted"])
    return JsonResponse({"deleted": True})


@require_auth(0, 1, 2, 3)
def blog_comments(request, blog_id):
    if request.method != "POST":
        return method_not_allowed("POST")
    blog = Blog.objects.filter(id=blog_id, is_deleted=False).first()
    if not blog:
        return error("blog not found", 404)
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    content = str(data.get("content", "")).strip()
    if not content:
        return error("comment content is required")
    comment = Comment.objects.create(
        blog=blog, user_id=int(request.claims["user_id"]), content=content
    )
    return JsonResponse({"comment_id": comment.id}, status=201)


@require_auth()
def comment_detail(request, comment_id):
    if request.method != "DELETE":
        return method_not_allowed("DELETE")
    comment = Comment.objects.filter(id=comment_id, is_deleted=False).first()
    if not comment:
        return error("comment not found", 404)
    if int(request.claims["usertype"]) != 3 and comment.user_id != int(
        request.claims["user_id"]
    ):
        return error("forbidden", 403)
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted"])
    return JsonResponse({"deleted": True})

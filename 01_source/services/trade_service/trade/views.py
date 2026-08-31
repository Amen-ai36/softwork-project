import secrets

from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.utils import timezone

from services.common.auth import require_auth
from services.common.client import resolve_usernames
from services.common.http import body, error, method_not_allowed
from services.trade_service.trade.models import CartItem, Food, GroupBuyCoupon, Order

FOOD_FIELDS = (
    "id",
    "name",
    "price",
    "image",
    "sale",
    "saleperson",
    "providor",
    "rating",
    "ratenum",
    "inf",
    "merchant_id",
    "is_off_shelf",
    "is_sold_out",
)
ORDER_FIELDS = (
    "id",
    "user_id",
    "rider_id",
    "food_id",
    "num",
    "cost",
    "address",
    "pos",
    "comment",
    "scoretofood",
    "scoretodeliver",
    "is_abnormal",
    "time",
)


def serialize(instance, fields):
    return {field: getattr(instance, field) for field in fields}


def parse_positive_int(value, name):
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed < 1:
        raise ValueError(f"{name} must be positive")
    return parsed


def sync_food_sales(food):
    order_totals = food.orders.aggregate(people=Sum("num"), orders=Sum("num"))
    coupon_totals = food.coupons.filter(status__in=(0, 1)).aggregate(copies=Sum("num"))
    food.sale = (order_totals["people"] or 0) + (coupon_totals["copies"] or 0)
    food.saleperson = (
        food.orders.count() + food.coupons.filter(status__in=(0, 1)).count()
    )
    food.save(update_fields=["sale", "saleperson"])


def foods(request):
    if request.method == "GET":
        keyword = request.GET.get("q", "").strip()
        queryset = Food.objects.filter(is_off_shelf=False)
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword)
                | Q(providor__icontains=keyword)
                | Q(inf__icontains=keyword)
            )
        return JsonResponse(
            {"foods": [serialize(item, FOOD_FIELDS) for item in queryset]}
        )
    if request.method != "POST":
        return method_not_allowed("GET", "POST")
    return create_food(request)


@require_auth(2)
def create_food(request):
    try:
        data = body(request)
        name = str(data.get("name", "")).strip()
        price = float(data.get("price"))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not name or price <= 0:
        return error("name and a positive price are required")
    food = Food.objects.create(
        name=name,
        price=price,
        image=str(data.get("image", "")),
        providor=str(data.get("providor", "")).strip() or name,
        inf=str(data.get("inf", "")),
        merchant_id=int(request.claims["user_id"]),
    )
    return JsonResponse({"food": serialize(food, FOOD_FIELDS)}, status=201)


def food_detail(request, food_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    food = Food.objects.filter(id=food_id, is_off_shelf=False).first()
    if not food:
        return error("food not found", 404)
    return JsonResponse({"food": serialize(food, FOOD_FIELDS)})


@require_auth(2, 3)
def food_status(request, food_id):
    if request.method != "PATCH":
        return method_not_allowed("PATCH")
    food = Food.objects.filter(id=food_id).first()
    if not food:
        return error("food not found", 404)
    if int(request.claims["usertype"]) != 3 and food.merchant_id != int(
        request.claims["user_id"]
    ):
        return error("forbidden", 403)
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    updates = []
    for field in ("is_off_shelf", "is_sold_out"):
        if field in data:
            if not isinstance(data[field], bool):
                return error(f"{field} must be a boolean")
            setattr(food, field, data[field])
            updates.append(field)
    if not updates:
        return error("no status field supplied")
    food.save(update_fields=updates)
    return JsonResponse({"food": serialize(food, FOOD_FIELDS)})


@require_auth(0)
def orders(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
        food_id = int(data.get("food_id"))
        num = parse_positive_int(data.get("num", 1), "num")
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    with transaction.atomic():
        food = Food.objects.select_for_update().filter(id=food_id).first()
        if not food or food.is_off_shelf:
            return error("food not found", 404)
        if food.is_sold_out:
            return error("food is sold out", 409)
        order = Order.objects.create(
            user_id=int(request.claims["user_id"]),
            food=food,
            num=num,
            cost=round(food.price * num, 2),
            address=str(data.get("address", ""))[:100],
        )
        sync_food_sales(food)
    return JsonResponse({"order": serialize(order, ORDER_FIELDS)}, status=201)


@require_auth()
def order_detail(request, order_id):
    if request.method != "GET":
        return method_not_allowed("GET")
    order = Order.objects.select_related("food").filter(id=order_id).first()
    if not order:
        return error("order not found", 404)
    claims_id = int(request.claims["user_id"])
    role = int(request.claims["usertype"])
    allowed = claims_id in (order.user_id, order.rider_id) or (
        role in (2, 3) and (role == 3 or order.food.merchant_id == claims_id)
    )
    if not allowed:
        return error("forbidden", 403)
    data = serialize(order, ORDER_FIELDS)
    user_ids = {order.user_id}
    if order.rider_id:
        user_ids.add(order.rider_id)
    usernames = resolve_usernames(user_ids)
    data["user_name"] = usernames.get(order.user_id, "匿名用户")
    if order.rider_id:
        data["rider_name"] = usernames.get(order.rider_id, "匿名用户")
    return JsonResponse({"order": data})


@require_auth(0)
def order_comment(request, order_id):
    if request.method != "POST":
        return method_not_allowed("POST")
    order = Order.objects.filter(id=order_id, user_id=request.claims["user_id"]).first()
    if not order:
        return error("order not found", 404)
    if order.pos not in (4, 5):
        return error("order is not ready for review", 409)
    try:
        data = body(request)
        food_score = float(data.get("scoretofood", 0))
        rider_score = float(data.get("scoretodeliver", 0))
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not (0 <= food_score <= 5 and 0 <= rider_score <= 5):
        return error("scores must be between 0 and 5")
    order.comment = str(data.get("comment", ""))[:200]
    order.scoretofood = round(food_score, 1)
    order.scoretodeliver = round(rider_score, 1)
    order.pos = 5
    order.save(update_fields=["comment", "scoretofood", "scoretodeliver", "pos"])
    reviews = order.food.orders.filter(scoretofood__gt=0)
    if reviews.exists():
        scores = [
            float(value) for value in reviews.values_list("scoretofood", flat=True)
        ]
        order.food.rating = round(sum(scores) / len(scores), 1)
        order.food.ratenum = len(scores)
        order.food.save(update_fields=["rating", "ratenum"])
    return JsonResponse({"order": serialize(order, ORDER_FIELDS)})


@require_auth(0)
def cart(request):
    user_id = int(request.claims["user_id"])
    if request.method == "GET":
        items = CartItem.objects.filter(user_id=user_id).select_related("food")
        return JsonResponse(
            {
                "items": [
                    {
                        "id": item.id,
                        "food_id": item.food_id,
                        "food_name": item.food.name,
                        "num": item.num,
                        "cost": item.cost,
                        "address": item.address,
                    }
                    for item in items
                ]
            }
        )
    if request.method != "POST":
        return method_not_allowed("GET", "POST")
    try:
        data = body(request)
        food = Food.objects.filter(
            id=int(data.get("food_id")), is_off_shelf=False
        ).first()
        num = parse_positive_int(data.get("num", 1), "num")
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not food or food.is_sold_out:
        return error("food unavailable", 409)
    item, _ = CartItem.objects.update_or_create(
        user_id=user_id,
        food=food,
        defaults={
            "num": num,
            "cost": food.price,
            "address": str(data.get("address", ""))[:100],
        },
    )
    return JsonResponse({"item_id": item.id}, status=201)


@require_auth(0)
def cart_item(request, item_id):
    item = CartItem.objects.filter(
        id=item_id, user_id=int(request.claims["user_id"])
    ).first()
    if not item:
        return error("cart item not found", 404)
    if request.method == "DELETE":
        item.delete()
        return JsonResponse({"deleted": True})
    if request.method != "PATCH":
        return method_not_allowed("PATCH", "DELETE")
    try:
        data = body(request)
        if "num" in data:
            item.num = parse_positive_int(data["num"], "num")
        if "address" in data:
            item.address = str(data["address"])[:100]
    except ValueError as exc:
        return error(str(exc))
    item.save(update_fields=["num", "address"])
    return JsonResponse({"item_id": item.id, "num": item.num})


@require_auth(0)
def cart_checkout(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    user_id = int(request.claims["user_id"])
    with transaction.atomic():
        items = list(
            CartItem.objects.select_for_update()
            .filter(user_id=user_id)
            .select_related("food")
        )
        if not items:
            return error("cart is empty", 409)
        if any(item.food.is_off_shelf or item.food.is_sold_out for item in items):
            return error("cart contains unavailable food", 409)
        created = [
            Order.objects.create(
                user_id=user_id,
                food=item.food,
                num=item.num,
                cost=round(item.food.price * item.num, 2),
                address=item.address,
            )
            for item in items
        ]
        foods_to_sync = {item.food for item in items}
        CartItem.objects.filter(id__in=[item.id for item in items]).delete()
        for food in foods_to_sync:
            sync_food_sales(food)
    return JsonResponse(
        {"orders": [serialize(order, ORDER_FIELDS) for order in created]}, status=201
    )


@require_auth(0)
def groupbuy(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
        food = Food.objects.filter(
            id=int(data.get("food_id")), is_off_shelf=False
        ).first()
        num = parse_positive_int(data.get("num", 1), "num")
    except (ValueError, TypeError) as exc:
        return error(str(exc))
    if not food or food.is_sold_out:
        return error("food unavailable", 409)
    coupon = GroupBuyCoupon.objects.create(
        user_id=int(request.claims["user_id"]),
        food=food,
        num=num,
        cost=round(food.price * num, 2),
        code=secrets.token_hex(5).upper(),
    )
    sync_food_sales(food)
    return JsonResponse(
        {"coupon": {"id": coupon.id, "code": coupon.code, "cost": coupon.cost}},
        status=201,
    )


@require_auth(2)
def groupbuy_redeem(request):
    if request.method != "POST":
        return method_not_allowed("POST")
    try:
        data = body(request)
    except ValueError as exc:
        return error(str(exc))
    coupon = (
        GroupBuyCoupon.objects.select_related("food")
        .filter(code=str(data.get("code", "")).upper())
        .first()
    )
    if not coupon:
        return error("coupon not found", 404)
    if coupon.food.merchant_id != int(request.claims["user_id"]):
        return error("forbidden", 403)
    if coupon.status != 0:
        return error("coupon is not redeemable", 409)
    coupon.status = 1
    coupon.used_at = timezone.now()
    coupon.save(update_fields=["status", "used_at"])
    return JsonResponse({"redeemed": True, "coupon_id": coupon.id})


@require_auth(1)
def rider_orders(request):
    if request.method != "GET":
        return method_not_allowed("GET")
    rider_id = int(request.claims["user_id"])
    queryset = Order.objects.filter(Q(pos=0) | Q(rider_id=rider_id)).order_by("time")
    orders = [serialize(order, ORDER_FIELDS) for order in queryset]
    usernames = resolve_usernames({order["user_id"] for order in orders})
    for order in orders:
        order["user_name"] = usernames.get(order["user_id"], "匿名用户")
    return JsonResponse({"orders": orders})


def transition_order(request, order_id, roles, expected, target, owner_check=None):
    if request.method != "POST":
        return method_not_allowed("POST")
    if int(request.claims["usertype"]) not in roles:
        return error("forbidden", 403)
    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .select_related("food")
            .filter(id=order_id)
            .first()
        )
        if not order:
            return error("order not found", 404)
        if owner_check and not owner_check(order, int(request.claims["user_id"])):
            return error("forbidden", 403)
        if order.pos != expected:
            return error(
                "invalid order state", 409, current=order.pos, expected=expected
            )
        order.pos = target
        if target == 1:
            order.rider_id = int(request.claims["user_id"])
            order.save(update_fields=["pos", "rider_id"])
        else:
            order.save(update_fields=["pos"])
    return JsonResponse({"order": serialize(order, ORDER_FIELDS)})


@require_auth(1)
def order_accept(request, order_id):
    return transition_order(request, order_id, (1,), 0, 1)


@require_auth(2)
def order_prepare(request, order_id):
    return transition_order(
        request,
        order_id,
        (2,),
        1,
        2,
        lambda order, user_id: order.food.merchant_id == user_id,
    )


@require_auth(1)
def order_pickup(request, order_id):
    return transition_order(
        request,
        order_id,
        (1,),
        2,
        3,
        lambda order, user_id: order.rider_id == user_id,
    )


@require_auth(1)
def order_deliver(request, order_id):
    return transition_order(
        request,
        order_id,
        (1,),
        3,
        4,
        lambda order, user_id: order.rider_id == user_id,
    )

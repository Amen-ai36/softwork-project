import json
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import resolve

from services.common.auth import issue_token
from services.common.contracts import PUBLIC_API_CONTRACTS, route_patterns
from services.trade_service.config.urls import urlpatterns
from services.trade_service.trade.models import Food, Order


class TradeApiTests(TestCase):
    merchant_id = 20
    user_id = 10
    rider_id = 30

    def setUp(self):
        self.food = Food.objects.create(
            name="宫保鸡丁",
            price=18.5,
            providor="测试商户",
            merchant_id=self.merchant_id,
        )

    def request(self, method, path, payload, user_id, role):
        return getattr(self.client, method)(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {issue_token(user_id, role)}",
        )

    def test_food_listing_is_public(self):
        response = self.client.get("/foods?q=宫保")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["foods"][0]["id"], self.food.id)

    def test_merchant_creates_and_updates_food(self):
        response = self.request(
            "post",
            "/foods",
            {"name": "红烧肉", "price": 28, "providor": "测试商户"},
            self.merchant_id,
            2,
        )
        self.assertEqual(response.status_code, 201)
        food_id = response.json()["food"]["id"]
        response = self.request(
            "patch",
            f"/foods/{food_id}/status",
            {"is_sold_out": True},
            self.merchant_id,
            2,
        )
        self.assertTrue(response.json()["food"]["is_sold_out"])

    def test_regular_user_cannot_create_food(self):
        response = self.request(
            "post",
            "/foods",
            {"name": "越权菜品", "price": 10},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 403)

    def test_sold_out_food_cannot_be_ordered(self):
        self.food.is_sold_out = True
        self.food.save(update_fields=["is_sold_out"])
        response = self.request(
            "post",
            "/orders",
            {"food_id": self.food.id, "num": 1},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 409)

    def test_order_delivery_state_machine(self):
        response = self.request(
            "post",
            "/orders",
            {"food_id": self.food.id, "num": 2, "address": "测试地址"},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 201)
        order_id = response.json()["order"]["id"]
        steps = [
            ("accept", self.rider_id, 1, 1),
            ("prepare", self.merchant_id, 2, 2),
            ("pickup", self.rider_id, 1, 3),
            ("deliver", self.rider_id, 1, 4),
        ]
        for action, user_id, role, expected in steps:
            response = self.request(
                "post", f"/orders/{order_id}/{action}", {}, user_id, role
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["order"]["pos"], expected)
        self.assertEqual(Order.objects.get(id=order_id).cost, 37.0)

    def test_delivery_transition_rejects_wrong_state(self):
        order = Order.objects.create(
            user_id=self.user_id,
            rider_id=self.rider_id,
            food=self.food,
            num=1,
            cost=self.food.price,
        )
        response = self.request(
            "post",
            f"/orders/{order.id}/pickup",
            {},
            self.rider_id,
            1,
        )
        self.assertEqual(response.status_code, 409)

    def test_groupbuy_can_only_be_redeemed_by_owner_merchant(self):
        response = self.request(
            "post",
            "/groupbuy",
            {"food_id": self.food.id, "num": 2},
            self.user_id,
            0,
        )
        code = response.json()["coupon"]["code"]
        denied = self.request(
            "post", "/groupbuy/redeem", {"code": code}, self.merchant_id + 1, 2
        )
        self.assertEqual(denied.status_code, 403)
        accepted = self.request(
            "post", "/groupbuy/redeem", {"code": code}, self.merchant_id, 2
        )
        self.assertEqual(accepted.status_code, 200)

    def test_cart_checkout_creates_orders_atomically(self):
        response = self.request(
            "post",
            "/cart",
            {"food_id": self.food.id, "num": 3, "address": "测试地址"},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 201)
        response = self.request("post", "/cart/checkout", {}, self.user_id, 0)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.get().num, 3)

    def test_cross_service_user_references_are_plain_ids(self):
        user_field = Order._meta.get_field("user_id")
        rider_field = Order._meta.get_field("rider_id")
        self.assertIsNone(user_field.remote_field)
        self.assertIsNone(rider_field.remote_field)

    def test_all_exposed_api_methods_match_contract(self):
        contract = set(PUBLIC_API_CONTRACTS["trade-service"])
        self.assertEqual(
            route_patterns(urlpatterns), {path for _method, path in contract}
        )
        covered = set()

        def call(method, path, payload=None, user_id=None, role=None):
            headers = {}
            if user_id is not None:
                headers["HTTP_AUTHORIZATION"] = f"Bearer {issue_token(user_id, role)}"
            request = getattr(self.client, method.lower())
            if payload is None:
                response = request(path, **headers)
            else:
                response = request(
                    path,
                    data=json.dumps(payload),
                    content_type="application/json",
                    **headers,
                )
            route = f"/{resolve(urlsplit(path).path).route}"
            covered.add((method, route))
            self.assertLess(response.status_code, 400, f"{method} {path}")
            return response

        call("GET", "/health/live")
        call("GET", "/health/ready")
        call("GET", "/health/version")
        call("GET", "/foods?q=测试")
        created_food = call(
            "POST",
            "/foods",
            {"name": "契约菜品", "price": 20, "providor": "契约商家"},
            self.merchant_id,
            2,
        )
        food_id = created_food.json()["food"]["id"]
        call("GET", f"/foods/{food_id}")
        call(
            "PATCH",
            f"/foods/{food_id}/status",
            {"is_sold_out": False},
            self.merchant_id,
            2,
        )
        created_order = call(
            "POST",
            "/orders",
            {"food_id": food_id, "num": 2, "address": "契约地址"},
            self.user_id,
            0,
        )
        order_id = created_order.json()["order"]["id"]
        call("GET", f"/orders/{order_id}", user_id=self.user_id, role=0)
        call("GET", "/rider/orders", user_id=self.rider_id, role=1)
        call(
            "POST",
            f"/orders/{order_id}/accept",
            {},
            self.rider_id,
            1,
        )
        call(
            "POST",
            f"/orders/{order_id}/prepare",
            {},
            self.merchant_id,
            2,
        )
        call(
            "POST",
            f"/orders/{order_id}/pickup",
            {},
            self.rider_id,
            1,
        )
        call(
            "POST",
            f"/orders/{order_id}/deliver",
            {},
            self.rider_id,
            1,
        )
        call(
            "POST",
            f"/orders/{order_id}/comment",
            {"scoretofood": 4.8, "scoretodeliver": 4.6, "comment": "很好"},
            self.user_id,
            0,
        )

        cart_item = call(
            "POST",
            "/cart",
            {"food_id": food_id, "num": 1, "address": "购物车地址"},
            self.user_id,
            0,
        )
        item_id = cart_item.json()["item_id"]
        call("GET", "/cart", user_id=self.user_id, role=0)
        call(
            "PATCH",
            f"/cart/{item_id}",
            {"num": 2},
            self.user_id,
            0,
        )
        call("DELETE", f"/cart/{item_id}", {}, self.user_id, 0)
        call(
            "POST",
            "/cart",
            {"food_id": food_id, "num": 1},
            self.user_id,
            0,
        )
        call("POST", "/cart/checkout", {}, self.user_id, 0)

        coupon = call(
            "POST",
            "/groupbuy",
            {"food_id": food_id, "num": 1},
            self.user_id,
            0,
        )
        call(
            "POST",
            "/groupbuy/redeem",
            {"code": coupon.json()["coupon"]["code"]},
            self.merchant_id,
            2,
        )
        self.assertEqual(covered, contract)

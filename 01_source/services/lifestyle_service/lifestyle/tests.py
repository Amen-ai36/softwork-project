import json
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import resolve

from services.common.auth import issue_token
from services.common.contracts import PUBLIC_API_CONTRACTS, route_patterns
from services.lifestyle_service.config.urls import urlpatterns
from services.lifestyle_service.lifestyle.models import Blog, Hotel, HotelOrder, Play


class LifestyleApiTests(TestCase):
    merchant_id = 20
    user_id = 10

    def request(self, method, path, payload, user_id, role):
        return getattr(self.client, method)(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {issue_token(user_id, role)}",
        )

    def test_hotel_create_book_and_review(self):
        response = self.request(
            "post",
            "/hotels",
            {
                "name": "云端酒店",
                "addr": "测试路 1 号",
                "price_day": 199,
                "price_clock": 59,
            },
            self.merchant_id,
            2,
        )
        self.assertEqual(response.status_code, 201)
        hotel_id = response.json()["hotel"]["id"]
        response = self.request(
            "post",
            "/hotel-orders",
            {
                "hotel_id": hotel_id,
                "room_type": "single_day",
                "duration": 2,
                "checkin_time": "2026-09-01T14:00:00+08:00",
            },
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 201)
        order_id = response.json()["order"]["id"]
        self.assertEqual(HotelOrder.objects.get(id=order_id).cost, 398)
        response = self.request(
            "post",
            f"/hotel-orders/{order_id}/comment",
            {"score": 4.8, "comment": "很好"},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(Hotel.objects.get(id=hotel_id).rating), 4.8)

    def test_play_booking(self):
        play = Play.objects.create(
            name="游乐园",
            addr="测试路 2 号",
            price=80,
            merchant_id=self.merchant_id,
        )
        response = self.request(
            "post",
            "/play-orders",
            {
                "play_id": play.id,
                "num": 3,
                "visit_time": "2026-09-01T09:00:00+08:00",
            },
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["order"]["cost"], 240)

    def test_blog_and_comment_lifecycle(self):
        response = self.request(
            "post",
            "/blogs",
            {"title": "周末记录", "content": "今天很好"},
            self.user_id,
            0,
        )
        blog_id = response.json()["blog_id"]
        response = self.request(
            "post",
            f"/blogs/{blog_id}/comments",
            {"content": "赞"},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 201)
        response = self.client.get(f"/blogs/{blog_id}")
        self.assertEqual(len(response.json()["comments"]), 1)
        response = self.request("delete", f"/blogs/{blog_id}", {}, self.user_id, 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Blog.objects.get(id=blog_id).is_deleted)

    def test_other_user_cannot_delete_blog(self):
        blog = Blog.objects.create(
            title="仅作者可删", content="content", author_id=self.user_id
        )
        response = self.request("delete", f"/blogs/{blog.id}", {}, self.user_id + 1, 0)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Blog.objects.get(id=blog.id).is_deleted)

    def test_regular_user_cannot_publish_hotel(self):
        response = self.request(
            "post",
            "/hotels",
            {"name": "越权酒店", "addr": "测试", "price_day": 100},
            self.user_id,
            0,
        )
        self.assertEqual(response.status_code, 403)

    def test_cross_service_references_are_plain_ids(self):
        self.assertIsNone(Hotel._meta.get_field("merchant_id").remote_field)
        self.assertIsNone(Blog._meta.get_field("author_id").remote_field)

    def test_all_exposed_api_methods_match_contract(self):
        contract = set(PUBLIC_API_CONTRACTS["lifestyle-service"])
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
        call("GET", "/hotels?q=契约")
        hotel = call(
            "POST",
            "/hotels",
            {"name": "契约酒店", "addr": "契约路 1 号", "price_day": 200},
            self.merchant_id,
            2,
        )
        hotel_id = hotel.json()["hotel"]["id"]
        call("GET", f"/hotels/{hotel_id}")
        hotel_order = call(
            "POST",
            "/hotel-orders",
            {
                "hotel_id": hotel_id,
                "room_type": "single_day",
                "duration": 1,
                "checkin_time": "2026-09-01T14:00:00+08:00",
            },
            self.user_id,
            0,
        )
        hotel_order_id = hotel_order.json()["order"]["id"]
        call(
            "GET",
            f"/hotel-orders/{hotel_order_id}",
            user_id=self.user_id,
            role=0,
        )
        call(
            "POST",
            f"/hotel-orders/{hotel_order_id}/comment",
            {"score": 4.8, "comment": "入住很好"},
            self.user_id,
            0,
        )

        call("GET", "/plays?q=契约")
        play = call(
            "POST",
            "/plays",
            {"name": "契约乐园", "addr": "契约路 2 号", "price": 80},
            self.merchant_id,
            2,
        )
        play_id = play.json()["play"]["id"]
        call("GET", f"/plays/{play_id}")
        play_order = call(
            "POST",
            "/play-orders",
            {
                "play_id": play_id,
                "num": 2,
                "visit_time": "2026-09-02T09:00:00+08:00",
            },
            self.user_id,
            0,
        )
        play_order_id = play_order.json()["order"]["id"]
        call(
            "GET",
            f"/play-orders/{play_order_id}",
            user_id=self.user_id,
            role=0,
        )
        call(
            "POST",
            f"/play-orders/{play_order_id}/comment",
            {"score": 4.6, "comment": "游玩很好"},
            self.user_id,
            0,
        )

        call("GET", "/blogs")
        blog = call(
            "POST",
            "/blogs",
            {"title": "契约博客", "content": "契约内容"},
            self.user_id,
            0,
        )
        blog_id = blog.json()["blog_id"]
        call("GET", f"/blogs/{blog_id}")
        comment = call(
            "POST",
            f"/blogs/{blog_id}/comments",
            {"content": "契约评论"},
            self.user_id,
            0,
        )
        call(
            "DELETE",
            f"/comments/{comment.json()['comment_id']}",
            {},
            self.user_id,
            0,
        )
        call("DELETE", f"/blogs/{blog_id}", {}, self.user_id, 0)
        self.assertEqual(covered, contract)

import json

from django.test import TestCase

from services.common.auth import issue_token
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

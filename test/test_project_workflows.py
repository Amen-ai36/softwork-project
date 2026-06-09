import json
import os
import shutil
import tempfile
from unittest.mock import patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_master.settings")

import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import resolve
from django.utils import timezone

django.setup()

from myapp.models import Blog, Comment, Food, GroupBuyCoupon, Hotel, HotelOrder, Order, Play, PlayOrder, User


class ProjectWorkflowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username="normal_user",
            password="abc12345",
            phone="13800000001",
            usertype=0,
        )
        cls.rider = User.objects.create(
            username="rider_user",
            password="abc12345",
            phone="13800000002",
            usertype=1,
        )
        cls.merchant = User.objects.create(
            username="merchant_user",
            password="abc12345",
            phone="13800000003",
            usertype=2,
        )
        cls.admin = User.objects.create(
            username="admin_user",
            password="abc12345",
            phone="13800000004",
            usertype=3,
        )
        cls.food = Food.objects.create(
            name="测试盖饭",
            price=18.5,
            image="images/food/1.jpg",
            providor="测试商家",
            inf="测试菜品",
            merchant=cls.merchant,
        )
        cls.hotel = Hotel.objects.create(
            name="测试酒店",
            addr="测试地址",
            price_clock=30,
            price_day=180,
            price_double_clock=50,
            price_double_day=260,
            price_special=320,
            image="images/hotel/1.jpg",
            inf="测试酒店简介",
            merchant=cls.merchant,
        )
        cls.play = Play.objects.create(
            name="测试乐园",
            addr="测试乐园地址",
            price=88,
            start_time="09:00",
            open_time="8h",
            image="images/play/1.png",
            inf="测试娱乐场所",
            merchant=cls.merchant,
        )

    def login_as(self, user):
        client = Client()
        session = client.session
        session["user_id"] = user.id
        session.save()
        return client

    def png_upload(self, name="upload.png"):
        return SimpleUploadedFile(
            name,
            b"\x89PNG\r\n\x1a\n",
            content_type="image/png",
        )

    def test_core_routes_resolve_to_expected_views(self):
        expected_routes = {
            "/index/": "index",
            "/account/login/": "login",
            "/account/register/": "register",
            "/food/": "food",
            "/fooddetails/": "fooddetails",
            "/foodorder/": "foodorder",
            "/groupbuyorder/": "groupbuyorder",
            "/hotel/": "hotel",
            "/hotelorder/": "hotelorder",
            "/play/": "play",
            "/playorder/": "playorder",
            "/rider/": "rider_orders",
            "/manage/": "admin_dashboard",
        }

        for path, view_name in expected_routes.items():
            with self.subTest(path=path):
                self.assertEqual(resolve(path).func.__name__, view_name)

    def test_register_login_and_role_redirects(self):
        client = Client()
        response = client.post(
            "/account/register/",
            {
                "username": "new_user",
                "password": "abc12345",
                "phone": "13800000005",
                "usertype": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")
        self.assertTrue(User.objects.filter(username="new_user", usertype=0).exists())

        response = client.post(
            "/account/login/",
            {"username": "new_user", "password": "abc12345", "usertype": "0"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/food/")

        response = Client().post(
            "/account/login/",
            {"username": self.rider.username, "password": self.rider.password, "usertype": "1"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/rider/")

        response = Client().post(
            "/account/login/",
            {"username": self.admin.username, "password": self.admin.password, "usertype": "3"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/manage/")

    def test_food_order_full_delivery_and_review_flow(self):
        user_client = self.login_as(self.user)
        rider_client = self.login_as(self.rider)
        merchant_client = self.login_as(self.merchant)

        response = user_client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "2", "address": "测试配送地址"},
        )
        self.assertEqual(response.status_code, 302)

        order = Order.objects.get(user=self.user, food=self.food)
        self.assertEqual(order.cost, 37.0)
        self.assertEqual(order.pos, 0)

        response = rider_client.get(f"/rider_accept/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        self.assertEqual(order.rider, self.rider)

        response = merchant_client.get(f"/merchant_prepare/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)

        response = rider_client.get(f"/rider_get/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 3)

        response = rider_client.get(f"/rider_deliver/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        response = user_client.post(
            f"/ordercomment/?orderid={order.id}",
            {"scoretofood": "4.5", "scoretodeliver": "5.0", "comment": "很好吃"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.scoretofood), "4.5")
        self.assertEqual(str(order.scoretodeliver), "5.0")

    def test_cross_role_food_order_visibility_and_response_flow(self):
        user_client = self.login_as(self.user)
        rider_client = self.login_as(self.rider)
        merchant_client = self.login_as(self.merchant)

        response = user_client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "1", "address": "跨端互动地址"},
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.user, food=self.food, address="跨端互动地址")
        self.assertEqual(order.pos, 0)

        response = rider_client.get("/rider/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "跨端互动地址")
        self.assertContains(response, "接单")

        response = rider_client.get(f"/rider_accept/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        self.assertEqual(order.rider, self.rider)

        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.rider.username)
        self.assertContains(response, "跨端互动地址")
        self.assertContains(response, "完成备餐")

        response = merchant_client.get(f"/merchant_prepare/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)

        response = rider_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)
        self.assertContains(response, "跨端互动地址")
        self.assertContains(response, "已取餐")

        response = rider_client.get(f"/rider_get/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 3)

        response = rider_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "配送中")
        self.assertContains(response, "已送达")

        response = rider_client.get(f"/rider_deliver/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        response = user_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)
        self.assertContains(response, "跨端互动地址")
        self.assertContains(response, "去评价")

    def test_food_listing_search_detail_order_status_and_space_queries(self):
        user_client = self.login_as(self.user)
        rider_client = self.login_as(self.rider)
        merchant_client = self.login_as(self.merchant)

        response = user_client.get("/food/", {"q": "盖饭"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)

        response = user_client.get("/fooddetails/", {"foodid": self.food.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)

        order = Order.objects.create(
            user=self.user,
            food=self.food,
            rider=self.rider,
            num=1,
            cost=self.food.price,
            address="查询测试地址",
            pos=3,
        )

        response = user_client.get("/orderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "骑手配送中")
        order.refresh_from_db()
        self.assertEqual(order.address, "查询测试地址")

        response = user_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

        response = rider_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)

        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)

    def test_group_buy_coupon_create_display_and_redeem_flow(self):
        user_client = self.login_as(self.user)
        merchant_client = self.login_as(self.merchant)

        response = user_client.get(f"/groupbuyorder/?foodid={self.food.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "到店团购下单")
        self.assertContains(response, self.food.name)

        response = user_client.post(f"/groupbuyorder/?foodid={self.food.id}", {"num": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "团购券生成成功")

        coupon = GroupBuyCoupon.objects.get(user=self.user, food=self.food)
        self.assertEqual(coupon.num, 2)
        self.assertEqual(coupon.cost, 37.0)
        self.assertEqual(coupon.status, 0)
        self.assertTrue(coupon.code)

        response = user_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "我的团购券")
        self.assertContains(response, coupon.code)
        self.assertContains(response, "待使用")

        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "团购券核销")
        self.assertContains(response, coupon.code)
        self.assertContains(response, self.user.username)

        response = merchant_client.post("/groupbuy/redeem/", {"code": coupon.code.lower()})
        self.assertEqual(response.status_code, 302)
        coupon.refresh_from_db()
        self.assertEqual(coupon.status, 1)
        self.assertIsNotNone(coupon.used_at)

        response = user_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "已使用")

        other_merchant = User.objects.create(
            username="coupon_seller2",
            password="abc12345",
            phone="13800000009",
            usertype=2,
        )
        other_food = Food.objects.create(
            name="其他商家的菜",
            price=12,
            image="images/food/1.jpg",
            providor="其他商家",
            inf="其他菜品",
            merchant=other_merchant,
        )
        other_coupon = GroupBuyCoupon.objects.create(
            user=self.user,
            food=other_food,
            num=1,
            cost=12,
            code="OTHER12345",
        )
        response = merchant_client.post("/groupbuy/redeem/", {"code": other_coupon.code})
        self.assertContains(response, "核销码不存在或不属于您的商品", status_code=200)

    def test_hotel_booking_and_review_flow(self):
        client = self.login_as(self.user)
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {
                "room_type": "single_day",
                "duration": "2",
                "checkin_time": "2026-06-10T15:30",
            },
        )
        self.assertEqual(response.status_code, 302)

        order = HotelOrder.objects.get(user=self.user, hotel=self.hotel)
        self.assertEqual(order.cost, 360)
        self.assertEqual(order.pos, 4)

        response = client.post(
            f"/hotelcomment/?orderid={order.id}",
            {"score": "4.0", "comment": "入住体验不错"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.hotel.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.score), "4.0")
        self.assertEqual(str(self.hotel.rating), "4.0")
        self.assertEqual(self.hotel.ratenum, 1)

    def test_hotel_listing_search_detail_order_status_and_permissions(self):
        user_client = self.login_as(self.user)
        other_client = self.login_as(
            User.objects.create(
                username="hotel_other_user",
                password="abc12345",
                phone="13800000007",
                usertype=0,
            )
        )

        response = user_client.get("/hotel/", {"q": "酒店"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hotel.name)

        response = user_client.get("/hoteldetails/", {"hotelid": self.hotel.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hotel.name)

        order = HotelOrder.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type="single_clock",
            duration=3,
            checkin_time=timezone.now(),
            cost=90,
            pos=4,
        )

        response = user_client.get("/hotelorderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "待评价")

        response = other_client.get("/hotelorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单", status_code=200)

    def test_play_ticket_order_and_review_flow(self):
        client = self.login_as(self.user)
        response = client.post(
            f"/playorder/?playid={self.play.id}",
            {"num": "3", "visit_time": "2026-06-11T09:00"},
        )
        self.assertEqual(response.status_code, 302)

        order = PlayOrder.objects.get(user=self.user, play=self.play)
        self.assertEqual(order.cost, 264)
        self.assertEqual(order.pos, 4)

        response = client.post(
            f"/playcomment/?orderid={order.id}",
            {"score": "4.5", "comment": "值得去"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.play.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.score), "4.5")
        self.assertEqual(str(self.play.rating), "4.5")
        self.assertEqual(self.play.ratenum, 1)

    def test_play_listing_search_detail_order_status_and_permissions(self):
        user_client = self.login_as(self.user)
        other_client = self.login_as(
            User.objects.create(
                username="play_other_user",
                password="abc12345",
                phone="13800000008",
                usertype=0,
            )
        )

        response = user_client.get("/play/", {"q": "乐园"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.play.name)

        response = user_client.get("/playdetails/", {"playid": self.play.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.play.name)

        order = PlayOrder.objects.create(
            user=self.user,
            play=self.play,
            num=2,
            visit_time=timezone.now(),
            cost=176,
            pos=4,
        )

        response = user_client.get("/playorderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "待评价")

        response = other_client.get("/playorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单", status_code=200)

    def test_blog_comment_and_delete_flow(self):
        client = self.login_as(self.user)
        response = client.post("/blogsend/", {"title": "测试博客", "content": "测试正文"})
        self.assertEqual(response.status_code, 302)

        blog = Blog.objects.get(authorid=self.user)
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "测试评论"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(blogid=blog)
        self.assertEqual(comment.content, "测试评论")

        response = client.delete(f"/blogcomment/delete/?commentid={comment.id}")
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertTrue(comment.isdeleted)

        response = client.delete(f"/blog/delete/?blogid={blog.id}")
        self.assertEqual(response.status_code, 200)
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

    def test_blog_listing_detail_and_search_queries(self):
        client = self.login_as(self.user)
        blog = Blog.objects.create(title="测试查询博客", content="可搜索内容", authorid=self.user)
        Comment.objects.create(blogid=blog, userid=self.rider.id, content="评论内容")

        response = client.get("/blog/", {"q": "查询"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)

        response = client.get("/blogsdetails/", {"blogid": blog.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)
        self.assertContains(response, "评论内容")

    def test_ai_chat_endpoint_uses_catalog_context_without_live_network(self):
        client = self.login_as(self.user)
        with patch("myapp.views.call_aliyun_llm", return_value="测试 AI 回复") as mock_call:
            response = client.post("/ai-chat/", {"user_input": "推荐一下"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "测试 AI 回复")
        self.assertIn(self.food.name, mock_call.call_args.kwargs["system_prompt"])

    def test_merchant_can_create_food_hotel_and_play_with_uploads(self):
        temp_dir = tempfile.mkdtemp()
        merchant_client = self.login_as(self.merchant)
        try:
            with override_settings(BASE_DIR=temp_dir):
                response = merchant_client.post(
                    "/foodsend/",
                    {
                        "name": "商家新增菜品",
                        "price": "26.5",
                        "providor": "新增商家",
                        "inf": "新增菜品简介",
                        "image": self.png_upload("food.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                food = Food.objects.get(name="商家新增菜品")
                self.assertEqual(food.merchant, self.merchant)
                self.assertTrue(food.image.startswith("images/food/"))

                response = merchant_client.post(
                    "/hotelsend/",
                    {
                        "name": "商家新增酒店",
                        "addr": "新增酒店地址",
                        "inf": "新增酒店简介",
                        "price_clock": "35",
                        "price_day": "188",
                        "price_double_clock": "55",
                        "price_double_day": "288",
                        "price_special": "388",
                        "image": self.png_upload("hotel.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                hotel = Hotel.objects.get(name="商家新增酒店")
                self.assertEqual(hotel.merchant, self.merchant)
                self.assertEqual(hotel.price_day, 188)

                response = merchant_client.post(
                    "/playsend/",
                    {
                        "name": "商家新增娱乐",
                        "addr": "新增娱乐地址",
                        "price": "66",
                        "start_time": "10:30",
                        "open_time": "6h",
                        "inf": "新增娱乐简介",
                        "image": self.png_upload("play.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                play = Play.objects.get(name="商家新增娱乐")
                self.assertEqual(play.merchant, self.merchant)
                self.assertEqual(play.price, 66)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_role_permissions_are_enforced(self):
        user_client = self.login_as(self.user)
        rider_client = self.login_as(self.rider)
        merchant_client = self.login_as(self.merchant)

        self.assertContains(user_client.get("/foodsend/"), "只有商家可以添加美食", status_code=200)
        self.assertContains(user_client.get("/rider/"), "只有骑手可以访问此页面", status_code=200)

        order = Order.objects.create(
            user=self.user,
            food=self.food,
            rider=self.rider,
            num=1,
            cost=self.food.price,
            address="测试地址",
            pos=1,
            time=timezone.now(),
        )
        other_merchant = User.objects.create(
            username="other_merchant",
            password="abc12345",
            phone="13800000006",
            usertype=2,
        )
        other_merchant_client = self.login_as(other_merchant)

        response = rider_client.get(f"/merchant_prepare/?orderid={order.id}")
        self.assertContains(response, "只有商家可以操作", status_code=200)

        response = other_merchant_client.get(f"/merchant_prepare/?orderid={order.id}")
        self.assertContains(response, "该订单无法操作或不属于您的商品", status_code=200)

        response = merchant_client.get(f"/merchant_prepare/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)

    def test_admin_dashboard_and_actions(self):
        admin_client = self.login_as(self.admin)
        normal_client = self.login_as(self.user)

        response = normal_client.get("/manage/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

        response = admin_client.get("/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin.username)

        response = admin_client.post(
            "/manage/users/action/",
            {"user_id": self.user.id, "action": "toggle_active"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.isDelete)

        order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="管理员测试地址",
            pos=2,
        )
        response = admin_client.post(
            "/manage/orders/action/",
            {"order_id": order.id, "action": "complete"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        blog = Blog.objects.create(title="待审核博客", content="内容", authorid=self.user)
        response = admin_client.post(
            "/manage/blogs/action/",
            {"item_type": "blog", "item_id": blog.id},
        )
        self.assertEqual(response.status_code, 302)
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

        response = admin_client.post("/manage/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

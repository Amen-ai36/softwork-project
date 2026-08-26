"""
集成 / API 测试（Integration & API Tests）
=========================================
测试对象：模块之间的调用、数据库访问和对外接口。
覆盖要求：每个接口/流程的主成功流程、备选流程和异常流程。

说明：
- 通过 Django 测试 Client 直接访问 URL（模拟 HTTP 调用），验证响应状态码、
  响应内容、数据库状态变化。
- 外部 AI 服务（阿里云 DashScope）在测试中一律 mock，不访问真实网络。
- 使用独立测试数据库（默认 SQLite，见 food_master/test_settings.py），
  不会污染真实业务数据。

追溯编号映射（详见 docs/追溯表.pdf）：
- INT-TC01：AuthApiTest
- INT-TC02：FoodApiTest、CrossModuleIntegrationTest
- INT-TC03：GroupBuyApiTest
- INT-TC04：HotelApiTest
- INT-TC05：PlayApiTest
- INT-TC06：FoodApiTest（merchant_food_action / 上传校验分支）
- INT-TC07：BlogApiTest
- INT-TC08：AiApiTest
- INT-TC09：AdminApiTest
"""

import json
import os
import tempfile
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_master.test_settings")

import django

django.setup()

from unittest.mock import patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.utils import timezone

from myapp.models import (
    Blog,
    Comment,
    Food,
    GroupBuyCoupon,
    Hotel,
    HotelOrder,
    Order,
    Play,
    PlayOrder,
    Temp,
    User,
)


class HealthApiTest(TestCase):
    """Deployment probes stay public and return machine-readable state."""

    def test_liveness_endpoint(self):
        response = self.client.get("/health/live/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_readiness_endpoint_checks_database(self):
        response = self.client.get("/health/ready/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ready")

    def test_version_endpoint_uses_environment(self):
        with patch.dict(os.environ, {"APP_VERSION": "test-sha"}):
            response = self.client.get("/health/version/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["version"], "test-sha")


class ApiTestCase(TestCase):
    """公共基类：预置四类角色与基础业务数据"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username="normal_user", password="abc12345", phone="13800000001", usertype=0
        )
        cls.rider = User.objects.create(
            username="rider_user", password="abc12345", phone="13800000002", usertype=1
        )
        cls.merchant = User.objects.create(
            username="merchant_user",
            password="abc12345",
            phone="13800000003",
            usertype=2,
        )
        cls.admin = User.objects.create(
            username="admin_user", password="abc12345", phone="13800000004", usertype=3
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
        return SimpleUploadedFile(name, b"\x89PNG\r\n\x1a\n", content_type="image/png")

    def json_payload(self, response, script_id):
        """解析模板中 json_script 输出的数据（中文会被转义，需还原后断言）"""
        import re

        m = re.search(
            rf'<script id="{script_id}" type="application/json">(.*?)</script>',
            response.content.decode("utf-8"),
            re.S,
        )
        self.assertIsNotNone(m, f"页面中未找到 {script_id} 数据块")
        return json.loads(m.group(1))


class AuthApiTest(ApiTestCase):
    """认证模块 API：注册 / 登录（主、备选、异常流程）"""

    def test_register_success_flow(self):
        """主流程：合法注册成功并跳转登录页，数据库生成用户"""
        response = self.client.post(
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

    def test_register_duplicate_username_rejected(self):
        """备选/异常流程：用户名已被占用时拒绝注册"""
        response = self.client.post(
            "/account/register/",
            {
                "username": self.user.username,
                "password": "abc12345",
                "phone": "13800000006",
                "usertype": "0",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户名已被注册")
        self.assertEqual(User.objects.filter(username=self.user.username).count(), 1)

    def test_register_weak_password_rejected(self):
        """异常流程：密码不满足 8-16 位且含字母数字时拒绝"""
        for bad_pwd in ("12345678", "abcdefgh", "abc12"):
            with self.subTest(pwd=bad_pwd):
                response = self.client.post(
                    "/account/register/",
                    {
                        "username": f"weak_{len(bad_pwd)}",
                        "password": bad_pwd,
                        "phone": "13800000007",
                        "usertype": "0",
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "密码必须在8-16位之间")

    def test_register_invalid_phone_rejected(self):
        """异常流程：手机号不是 11 位数字时拒绝"""
        response = self.client.post(
            "/account/register/",
            {
                "username": "badphone",
                "password": "abc12345",
                "phone": "123",
                "usertype": "0",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "手机号必须是11位数字")

    def test_register_admin_role_forbidden(self):
        """异常流程：不允许通过注册页注册管理员账号"""
        response = self.client.post(
            "/account/register/",
            {
                "username": "hacker",
                "password": "abc12345",
                "phone": "13800000008",
                "usertype": "3",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用户类型只能为普通用户、骑手或商家")
        self.assertFalse(User.objects.filter(username="hacker").exists())

    def test_login_success_and_role_redirects(self):
        """主流程：各角色登录成功后跳转到对应首页"""
        cases = [
            (self.user, "/food/"),
            (self.rider, "/rider/"),
            (self.merchant, "/food/"),
            (self.admin, "/manage/"),
        ]
        for user, expected_url in cases:
            with self.subTest(user=user.username):
                response = Client().post(
                    "/account/login/",
                    {
                        "username": user.username,
                        "password": user.password,
                        "usertype": str(user.usertype),
                    },
                )
                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.url, expected_url)

    def test_login_wrong_password_rejected(self):
        """异常流程：密码错误时拒绝登录"""
        response = Client().post(
            "/account/login/",
            {"username": self.user.username, "password": "wrongpass1", "usertype": "0"},
        )
        self.assertContains(response, "用户名或者密码错误")

    def test_login_wrong_role_rejected(self):
        """异常流程：身份选择与账号不符时拒绝登录"""
        response = Client().post(
            "/account/login/",
            {
                "username": self.user.username,
                "password": self.user.password,
                "usertype": "1",
            },
        )
        self.assertContains(response, "用户的身份选择错误")

    def test_login_disabled_account_rejected(self):
        """异常流程：被停用账号拒绝登录"""
        disabled = User.objects.create(
            username="disabled_user",
            password="abc12345",
            phone="13800000009",
            usertype=0,
            isDelete=True,
        )
        response = Client().post(
            "/account/login/",
            {
                "username": disabled.username,
                "password": disabled.password,
                "usertype": "0",
            },
        )
        self.assertContains(response, "该账号已被停用")

    def test_login_missing_or_invalid_fields(self):
        """异常流程：缺少字段 / 非法身份值"""
        response = Client().post("/account/login/", {"username": "", "password": ""})
        self.assertContains(response, "请填写用户名和密码")

        response = Client().post(
            "/account/login/",
            {
                "username": self.user.username,
                "password": self.user.password,
                "usertype": "9",
            },
        )
        self.assertContains(response, "请选择身份")

    def test_logout_clears_session(self):
        """主流程：退出登录后 session 被清空，再访问受限页被重定向"""
        client = self.login_as(self.user)
        response = client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")
        response = client.get("/food/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")


class FoodApiTest(ApiTestCase):
    """美食模块 API：列表、搜索、详情、下单（主、备选、异常流程）"""

    def test_food_list_and_search(self):
        """主流程：列表返回 200 且包含菜品；备选流程：关键词搜索命中"""
        client = self.login_as(self.user)
        response = client.get("/food/")
        self.assertEqual(response.status_code, 200)
        payload = self.json_payload(response, "foods-data")
        self.assertIn(self.food.name, [f["name"] for f in payload])

        response = client.get("/food/", {"q": "盖饭"})
        self.assertEqual(response.status_code, 200)
        payload = self.json_payload(response, "foods-data")
        self.assertIn(self.food.name, [f["name"] for f in payload])

        response = client.get("/food/", {"q": "不存在的关键词xyz"})
        payload = self.json_payload(response, "foods-data")
        self.assertNotIn(self.food.name, [f["name"] for f in payload])

    def test_food_requires_login(self):
        """异常流程：未登录访问美食列表被重定向"""
        response = Client().get("/food/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")

    def test_food_detail_success_and_branches(self):
        """主流程：详情页正常；异常分支：缺参、不存在、已下架"""
        client = self.login_as(self.user)
        response = client.get("/fooddetails/", {"foodid": self.food.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.food.name)

        response = client.get("/fooddetails/")
        self.assertContains(response, "参数错误")

        response = client.get("/fooddetails/", {"foodid": 999999})
        self.assertContains(response, "食物不存在")

        off = Food.objects.create(
            name="下架菜",
            price=10,
            image="x",
            providor="p",
            merchant=self.merchant,
            is_off_shelf=True,
        )
        response = client.get("/fooddetails/", {"foodid": off.id})
        self.assertContains(response, "该商品已下架")

    def test_foodorder_immediate_order_creates_order(self):
        """主流程：立即下单（cutlery=1）生成 Order，金额=单价×数量"""
        client = self.login_as(self.user)
        response = client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "2", "address": "测试配送地址", "cutlery": "1"},
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.user, food=self.food)
        self.assertEqual(order.num, 2)
        self.assertAlmostEqual(order.cost, 37.0)
        self.assertEqual(order.pos, 0)

    def test_foodorder_add_to_cart_creates_temp(self):
        """备选流程：加入购物车（cutlery=2）创建 Temp 购物车记录"""
        client = self.login_as(self.user)
        response = client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "3", "address": "购物车地址", "cutlery": "2"},
        )
        self.assertEqual(response.status_code, 302)
        temp = Temp.objects.get(user=self.user, food=self.food)
        self.assertEqual(temp.num, 3)
        self.assertAlmostEqual(temp.cost, self.food.price)  # 购物车存单价
        self.assertEqual(temp.pos, 0)

    def test_foodorder_validation_branches(self):
        """异常流程：缺参 / 售罄 / 下架 / 不存在"""
        client = self.login_as(self.user)
        response = client.post(f"/foodorder/?foodid={self.food.id}", {"num": "1"})
        self.assertContains(response, "请填写完整的下单信息")

        sold = Food.objects.create(
            name="售罄菜",
            price=10,
            image="x",
            providor="p",
            merchant=self.merchant,
            is_sold_out=True,
        )
        response = client.post(
            f"/foodorder/?foodid={sold.id}",
            {"num": "1", "address": "a", "cutlery": "1"},
        )
        self.assertContains(response, "该商品已售罄")

        response = client.post(
            f"/foodorder/?foodid=999999", {"num": "1", "address": "a", "cutlery": "1"}
        )
        self.assertContains(response, "食物不存在")

        # 异常：缺少 foodid 参数
        response = client.post(
            "/foodorder/", {"num": "1", "address": "a", "cutlery": "1"}
        )
        self.assertContains(response, "参数错误")

        for bad_num in ("0", "-1", "abc"):
            with self.subTest(num=bad_num):
                response = client.post(
                    f"/foodorder/?foodid={self.food.id}",
                    {"num": bad_num, "address": "a", "cutlery": "1"},
                )
                self.assertIn("购买数量", response.content.decode())

        response = client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "1", "address": "a", "cutlery": "unexpected"},
        )
        self.assertContains(response, "请选择立即下单或加入购物车")

    def test_cart_update_delete_clear_api(self):
        """购物车 API：更新（主）、删除（主）、清空下单（主）、未登录/不存在（异常）"""
        client = self.login_as(self.user)
        # 加入购物车
        client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "2", "address": "购物车地址", "cutlery": "2"},
        )
        temp = Temp.objects.get(user=self.user, food=self.food)

        # 主流程：更新数量 → 金额 = 单价×数量
        response = client.post(
            f"/cart/update/{temp.id}/",
            data=json.dumps({"num": 4}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["num"], 4)
        self.assertAlmostEqual(response.json()["cost"], self.food.price * 4)

        # 主流程：清空购物车 → 生成 Order，Temp 被删除
        response = client.post("/cart/clear/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        order = Order.objects.get(user=self.user, food=self.food)
        self.assertEqual(order.num, 4)
        self.assertAlmostEqual(order.cost, self.food.price * 4)
        self.assertFalse(Temp.objects.filter(user=self.user).exists())

        # 异常流程：清空空购物车返回友好提示
        response = client.post("/cart/clear/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("购物车已是空的", response.json().get("msg", ""))

        # 异常流程：未登录更新购物车 → 401
        response = Client().post(
            "/cart/update/999999/",
            data=json.dumps({"num": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # 异常流程：不存在的购物车项 → 404
        response = client.post(
            "/cart/update/999999/",
            data=json.dumps({"num": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

        client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "1", "address": "a", "cutlery": "2"},
        )
        temp = Temp.objects.get(user=self.user, food=self.food)
        for payload, expected in [
            ({"num": 0}, "数量必须大于0"),
            ({"num": "bad"}, "数量必须是正整数"),
            ({"address": "   "}, "配送地址不能为空"),
        ]:
            with self.subTest(payload=payload):
                response = client.post(
                    f"/cart/update/{temp.id}/",
                    data=json.dumps(payload),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(expected, response.json()["msg"])

        # 异常流程：GET 方式删除 → 405
        response = Client().get("/cart/delete/999999/")
        self.assertEqual(response.status_code, 405)

        # 异常分支：购物车存在已下架/售罄商品时清空被拒绝
        client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "1", "address": "a", "cutlery": "2"},
        )
        self.food.is_off_shelf = True
        self.food.save(update_fields=["is_off_shelf"])
        response = client.post("/cart/clear/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertIn("已下架或售罄", response.json()["msg"])
        self.food.is_off_shelf = False
        self.food.save(update_fields=["is_off_shelf"])

    def test_food_order_visibility_and_review_state_are_enforced(self):
        owner = self.login_as(self.user)
        stranger = User.objects.create(
            username="food_stranger",
            password="abc12345",
            phone="13800000021",
            usertype=0,
        )
        stranger_client = self.login_as(stranger)
        order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="隐私测试地址",
            pos=3,
        )

        self.assertContains(
            stranger_client.get("/orderpos/", {"orderid": order.id}), "无权查看该订单"
        )
        self.assertContains(
            stranger_client.post(
                f"/ordercomment/?orderid={order.id}",
                {"scoretofood": "5", "scoretodeliver": "5", "comment": "越权"},
            ),
            "无权评价该订单",
        )
        self.assertContains(
            owner.post(
                f"/ordercomment/?orderid={order.id}",
                {"scoretofood": "5", "scoretodeliver": "5", "comment": "过早评价"},
            ),
            "该订单当前不可评价",
        )

        order.pos = 4
        order.save(update_fields=["pos"])
        response = owner.post(
            f"/ordercomment/?orderid={order.id}",
            {"scoretofood": "4.5", "scoretodeliver": "5", "comment": "首次评价"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 5)

        response = owner.post(
            f"/ordercomment/?orderid={order.id}",
            {"scoretofood": "1", "scoretodeliver": "1", "comment": "重复评价"},
        )
        self.assertContains(response, "该订单当前不可评价")
        order.refresh_from_db()
        self.assertEqual(str(order.scoretofood), "4.5")
        self.assertEqual(order.comment, "首次评价")

    def test_merchant_food_action_toggles(self):
        """商家商品管理 API：下架/售罄切换（主）、权限与归属（异常）"""
        client = self.login_as(self.user)
        self.assertContains(
            client.post(
                "/merchant/food/action/",
                {"food_id": self.food.id, "action": "toggle_off_shelf"},
            ),
            "只有商家可以管理商品状态",
        )

        merchant_client = self.login_as(self.merchant)
        response = merchant_client.post(
            "/merchant/food/action/",
            {"food_id": self.food.id, "action": "toggle_off_shelf"},
        )
        self.assertEqual(response.status_code, 302)
        self.food.refresh_from_db()
        self.assertTrue(self.food.is_off_shelf)

        response = merchant_client.post(
            "/merchant/food/action/",
            {"food_id": self.food.id, "action": "toggle_sold_out"},
        )
        self.food.refresh_from_db()
        self.assertTrue(self.food.is_sold_out)

        # 异常：操作别人的商品
        other = User.objects.create(
            username="other_seller",
            password="abc12345",
            phone="13800000011",
            usertype=2,
        )
        other_client = self.login_as(other)
        response = other_client.post(
            "/merchant/food/action/",
            {"food_id": self.food.id, "action": "toggle_off_shelf"},
        )
        self.assertContains(response, "商品不存在或不属于当前商家")

        # 异常：不支持的操作
        response = merchant_client.post(
            "/merchant/food/action/", {"food_id": self.food.id, "action": "delete"}
        )
        self.assertContains(response, "不支持的商品操作")


class GroupBuyApiTest(ApiTestCase):
    """到店团购 API：下单、核销（主、备选、异常流程）"""

    def test_groupbuy_create_and_redeem_flow(self):
        """主流程：生成团购券 → 商家核销成功"""
        user_client = self.login_as(self.user)
        merchant_client = self.login_as(self.merchant)

        response = user_client.get(f"/groupbuyorder/?foodid={self.food.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "到店团购下单")

        response = user_client.post(
            f"/groupbuyorder/?foodid={self.food.id}", {"num": "2"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "团购券生成成功")

        coupon = GroupBuyCoupon.objects.get(user=self.user, food=self.food)
        self.assertEqual(coupon.num, 2)
        self.assertAlmostEqual(coupon.cost, 37.0)
        self.assertEqual(coupon.status, 0)
        self.assertRegex(coupon.code, r"^[0-9A-F]{10}$")
        self.food.refresh_from_db()
        self.assertEqual(self.food.sale, 2)
        self.assertEqual(self.food.saleperson, 1)

        response = merchant_client.post(
            "/groupbuy/redeem/", {"code": coupon.code.lower()}
        )
        self.assertEqual(response.status_code, 302)
        coupon.refresh_from_db()
        self.assertEqual(coupon.status, 1)
        self.assertIsNotNone(coupon.used_at)

    def test_groupbuy_validation_branches(self):
        """异常流程：空数量 / 0 / 负数 / 非数字"""
        client = self.login_as(self.user)
        for bad in (None, "0", "-1", "abc"):
            with self.subTest(bad=bad):
                data = {"num": bad} if bad is not None else {}
                response = client.post(f"/groupbuyorder/?foodid={self.food.id}", data)
                self.assertEqual(response.status_code, 200)
                self.assertIn("团购数量", response.content.decode())

    def test_groupbuy_redeem_exception_branches(self):
        """异常流程：非商家不可核销 / 空码 / 不属于自己的券 / 重复核销"""
        user_client = self.login_as(self.user)
        # 非商家
        response = user_client.post("/groupbuy/redeem/", {"code": "AAAABBBBCC"})
        self.assertContains(response, "只有商家可以核销团购券")

        merchant_client = self.login_as(self.merchant)
        # 空码
        response = merchant_client.post("/groupbuy/redeem/", {"code": ""})
        self.assertContains(response, "请输入核销码")

        # 不属于自己的券
        other = User.objects.create(
            username="other_seller2",
            password="abc12345",
            phone="13800000012",
            usertype=2,
        )
        other_food = Food.objects.create(
            name="别家菜", price=12, image="x", providor="p", merchant=other
        )
        other_coupon = GroupBuyCoupon.objects.create(
            user=self.user, food=other_food, num=1, cost=12, code="OTHER12345"
        )
        response = merchant_client.post(
            "/groupbuy/redeem/", {"code": other_coupon.code}
        )
        self.assertContains(response, "核销码不存在或不属于您的商品")

        # 重复核销
        mine = GroupBuyCoupon.objects.create(
            user=self.user, food=self.food, num=1, cost=18.5, code="MINE123456"
        )
        response = merchant_client.post("/groupbuy/redeem/", {"code": mine.code})
        self.assertEqual(response.status_code, 302)
        response = merchant_client.post("/groupbuy/redeem/", {"code": mine.code})
        self.assertContains(response, "该团购券已核销")


class HotelApiTest(ApiTestCase):
    """酒店模块 API：列表/搜索/详情/预订/评价/权限（主、备选、异常流程）"""

    def test_hotel_list_search_detail(self):
        """主流程：列表、搜索、详情"""
        client = self.login_as(self.user)
        response = client.get("/hotel/")
        self.assertEqual(response.status_code, 200)
        payload = self.json_payload(response, "hotels-data")
        self.assertIn(self.hotel.name, [h["name"] for h in payload])

        response = client.get("/hotel/", {"q": "酒店"})
        payload = self.json_payload(response, "hotels-data")
        self.assertIn(self.hotel.name, [h["name"] for h in payload])

        response = client.get("/hoteldetails/", {"hotelid": self.hotel.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.hotel.name)

    def test_hotel_booking_main_and_abnormal(self):
        """主流程：预订成功金额=单价×时长；异常：缺参/非法时长/非法时间/未知房型"""
        client = self.login_as(self.user)
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {
                "room_type": "single_day",
                "duration": "2",
                "checkin_time": "2026-06-20T15:30",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = HotelOrder.objects.get(user=self.user, hotel=self.hotel)
        self.assertEqual(order.cost, 360)
        self.assertEqual(order.pos, 4)
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.orders, 1)

        # 钟点房：single_clock 30 * 3
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {
                "room_type": "single_clock",
                "duration": "3",
                "checkin_time": "2026-06-20T15:30",
            },
        )
        order2 = HotelOrder.objects.order_by("-id").first()
        self.assertEqual(order2.cost, 90)

        # 异常：未知房型
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {"room_type": "vip", "duration": "1", "checkin_time": "2026-06-20T15:30"},
        )
        self.assertContains(response, "所选房型不存在")

        # 异常：时长非法
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {
                "room_type": "single_day",
                "duration": "0",
                "checkin_time": "2026-06-20T15:30",
            },
        )
        self.assertContains(response, "入住时间长度必须大于0")

        # 异常：时间格式错误
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {"room_type": "single_day", "duration": "1", "checkin_time": "not-a-time"},
        )
        self.assertContains(response, "入住时间格式不正确")

        # 异常：缺字段
        response = client.post(
            f"/hotelorder/?hotelid={self.hotel.id}", {"duration": "1"}
        )
        self.assertContains(response, "请填写完整的订房信息")

    def test_hotel_review_and_permission(self):
        """主流程：评价成功更新评分；异常：无权评价他人订单"""
        owner = self.login_as(self.user)
        other = User.objects.create(
            username="other_hotel_user",
            password="abc12345",
            phone="13800000013",
            usertype=0,
        )
        owner.post(
            f"/hotelorder/?hotelid={self.hotel.id}",
            {
                "room_type": "single_day",
                "duration": "1",
                "checkin_time": "2026-06-20T15:30",
            },
        )
        order = HotelOrder.objects.get(user=self.user, hotel=self.hotel)

        response = owner.post(
            f"/hotelcomment/?orderid={order.id}", {"score": "4.0", "comment": "不错"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.hotel.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.score), "4.0")
        self.assertEqual(str(self.hotel.rating), "4.0")
        self.assertEqual(self.hotel.ratenum, 1)

        # 异常：他人不能评价
        other_client = self.login_as(other)
        order2 = HotelOrder.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type="single_day",
            duration=1,
            checkin_time=timezone.now(),
            cost=180,
            pos=4,
        )
        response = other_client.post(
            f"/hotelcomment/?orderid={order2.id}", {"score": "5.0", "comment": "x"}
        )
        self.assertContains(response, "无权评价该订单")

        # 异常：评分越界
        response = owner.post(
            f"/hotelcomment/?orderid={order2.id}", {"score": "5.5", "comment": "x"}
        )
        self.assertContains(response, "评分必须大于0.0")

    def test_hotel_orderpos_visibility(self):
        """主流程：本人可查订单状态；异常：他人查看被拒"""
        user_client = self.login_as(self.user)
        User.objects.create(
            username="stranger1", password="abc12345", phone="13800000014", usertype=0
        )
        order = HotelOrder.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type="single_day",
            duration=1,
            checkin_time=timezone.now(),
            cost=180,
            pos=4,
        )
        response = user_client.get("/hotelorderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "待评价")

        stranger = self.login_as(User.objects.get(username="stranger1"))
        response = stranger.get("/hotelorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单")


class PlayApiTest(ApiTestCase):
    """娱乐模块 API：列表/搜索/详情/购票/评价/权限（主、备选、异常流程）"""

    def test_play_list_search_detail(self):
        client = self.login_as(self.user)
        response = client.get("/play/")
        self.assertEqual(response.status_code, 200)
        payload = self.json_payload(response, "plays-data")
        self.assertIn(self.play.name, [p["name"] for p in payload])

        response = client.get("/play/", {"q": "乐园"})
        payload = self.json_payload(response, "plays-data")
        self.assertIn(self.play.name, [p["name"] for p in payload])

        response = client.get("/playdetails/", {"playid": self.play.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.play.name)

    def test_play_order_main_and_abnormal(self):
        client = self.login_as(self.user)
        response = client.post(
            f"/playorder/?playid={self.play.id}",
            {"num": "3", "visit_time": "2026-06-21T09:00"},
        )
        self.assertEqual(response.status_code, 302)
        order = PlayOrder.objects.get(user=self.user, play=self.play)
        self.assertEqual(order.cost, 264)
        self.assertEqual(order.pos, 4)
        self.play.refresh_from_db()
        self.assertEqual(self.play.orders, 1)

        # 异常：数量非法
        for bad in ("0", "-1", "abc"):
            with self.subTest(bad=bad):
                response = client.post(
                    f"/playorder/?playid={self.play.id}",
                    {"num": bad, "visit_time": "2026-06-21T09:00"},
                )
                self.assertIn("票数", response.content.decode())

        # 异常：时间格式错误
        response = client.post(
            f"/playorder/?playid={self.play.id}", {"num": "1", "visit_time": "bad"}
        )
        self.assertContains(response, "预定时间格式不正确")

        # 异常：缺字段
        response = client.post(f"/playorder/?playid={self.play.id}", {"num": "1"})
        self.assertContains(response, "请填写完整的购票信息")

    def test_play_review_and_permission(self):
        owner = self.login_as(self.user)
        stranger = User.objects.create(
            username="stranger2", password="abc12345", phone="13800000015", usertype=0
        )
        owner.post(
            f"/playorder/?playid={self.play.id}",
            {"num": "2", "visit_time": "2026-06-21T09:00"},
        )
        order = PlayOrder.objects.get(user=self.user, play=self.play)

        response = owner.post(
            f"/playcomment/?orderid={order.id}", {"score": "4.5", "comment": "好玩"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.play.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(self.play.rating), "4.5")
        self.assertEqual(self.play.ratenum, 1)

        order2 = PlayOrder.objects.create(
            user=self.user,
            play=self.play,
            num=1,
            visit_time=timezone.now(),
            cost=88,
            pos=4,
        )
        response = self.login_as(stranger).post(
            f"/playcomment/?orderid={order2.id}", {"score": "5.0", "comment": "x"}
        )
        self.assertContains(response, "无权评价该订单")

        response = owner.post(
            f"/playcomment/?orderid={order2.id}", {"score": "0", "comment": "x"}
        )
        self.assertContains(response, "评分必须大于0.0")

    def test_play_orderpos_visibility(self):
        user_client = self.login_as(self.user)
        stranger = User.objects.create(
            username="stranger3", password="abc12345", phone="13800000016", usertype=0
        )
        order = PlayOrder.objects.create(
            user=self.user,
            play=self.play,
            num=1,
            visit_time=timezone.now(),
            cost=88,
            pos=4,
        )
        response = user_client.get("/playorderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "待评价")

        response = self.login_as(stranger).get("/playorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单")


class BlogApiTest(ApiTestCase):
    """博客模块 API：发布 / 列表 / 详情 / AJAX 评论 / 删除（主、异常流程）"""

    def test_blog_publish_list_detail(self):
        client = self.login_as(self.user)
        response = client.post(
            "/blogsend/", {"title": "测试博客", "content": "测试正文"}
        )
        self.assertEqual(response.status_code, 302)
        blog = Blog.objects.get(authorid=self.user)
        self.assertEqual(blog.title, "测试博客")

        response = client.get("/blog/", {"q": "测试"})
        self.assertContains(response, blog.title)

        response = client.get("/blogsdetails/", {"blogid": blog.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, blog.title)

        # 异常：标题或内容为空
        response = client.post("/blogsend/", {"title": "", "content": ""})
        self.assertContains(response, "标题和内容不能为空")

        # 异常：博客不存在
        response = client.get("/blogsdetails/", {"blogid": 999999})
        self.assertContains(response, "博客不存在")

    def test_blog_comment_ajax_main_and_abnormal(self):
        client = self.login_as(self.user)
        blog = Blog.objects.create(title="评论目标", content="内容", authorid=self.user)

        # 主流程：AJAX 评论成功
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "第一条评论"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        comment = Comment.objects.get(blogid=blog)
        self.assertEqual(comment.content, "第一条评论")
        self.assertEqual(comment.userid, self.user.id)

        # 异常：空内容
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("评论内容不能为空", response.json()["error"])

        # 异常：超长内容（>500 字）
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "长" * 501}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # 异常：博客不存在
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": 999999, "content": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

        # 异常：已逻辑删除的博客不可继续评论
        blog.isdeleted = True
        blog.save(update_fields=["isdeleted"])
        response = client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.filter(blogid=blog).count(), 1)

        # 异常：非法 JSON
        response = client.post(
            "/blogcomment/", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

        # 异常：未登录
        response = Client().post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_blog_delete_main_and_abnormal(self):
        client = self.login_as(self.user)
        blog = Blog.objects.create(title="待删博客", content="内容", authorid=self.user)
        comment = Comment.objects.create(
            blogid=blog, userid=self.user.id, content="待删评论"
        )

        # 主流程：删除评论（逻辑删除）
        response = client.delete(f"/blogcomment/delete/?commentid={comment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        comment.refresh_from_db()
        self.assertTrue(comment.isdeleted)

        # 主流程：删除博客（逻辑删除）
        response = client.delete(f"/blog/delete/?blogid={blog.id}")
        self.assertEqual(response.status_code, 200)
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

        # 异常：删除别人的博客 → 404
        blog2 = Blog.objects.create(
            title="别人的博客", content="内容", authorid=self.admin
        )
        response = client.delete(f"/blog/delete/?blogid={blog2.id}")
        self.assertEqual(response.status_code, 404)

        # 异常：错误请求方法 → 405
        response = client.get("/blog/delete/")
        self.assertEqual(response.status_code, 405)


class AiApiTest(ApiTestCase):
    """AI 助手 API：主成功流程与异常流程（外部调用全部 mock）"""

    def setUp(self):
        cache.clear()

    def test_ai_chat_main_flow_with_catalog_context(self):
        """主流程：返回 AI 回复，系统提示词包含平台菜品/酒店/娱乐信息"""
        client = self.login_as(self.user)
        with patch(
            "myapp.views.call_aliyun_llm", return_value="测试 AI 回复"
        ) as mock_call:
            response = client.post("/ai-chat/", {"user_input": "推荐一下"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "测试 AI 回复")
        prompt = mock_call.call_args.kwargs["system_prompt"]
        self.assertIn(self.food.name, prompt)
        self.assertIn(self.hotel.name, prompt)
        self.assertIn(self.play.name, prompt)

    def test_ai_chat_empty_input_rejected(self):
        """异常流程：空输入返回 400"""
        client = self.login_as(self.user)
        response = client.post("/ai-chat/", {"user_input": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "输入不能为空")

    def test_ai_chat_requires_login(self):
        """异常流程：未登录被重定向到首页"""
        response = Client().post("/ai-chat/", {"user_input": "推荐"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")

    def test_ai_chat_service_failure_returns_500(self):
        """异常流程：外部模型返回 None 时返回 500 友好错误"""
        client = self.login_as(self.user)
        with patch("myapp.views.call_aliyun_llm", return_value=None):
            response = client.post("/ai-chat/", {"user_input": "推荐"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("AI 服务暂时不可用", response.json()["error"])


class AdminApiTest(ApiTestCase):
    """管理后台 API：仪表盘、用户/订单/内容操作（主、备选、异常流程）"""

    def test_admin_dashboard_access_control(self):
        """主流程：管理员可访问；异常：普通用户被重定向"""
        normal = self.login_as(self.user)
        response = normal.get("/manage/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

        admin = self.login_as(self.admin)
        response = admin.get("/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.admin.username)

    def test_admin_user_actions(self):
        """主流程：停用用户；异常：不能停用自己、非法角色"""
        admin = self.login_as(self.admin)
        response = admin.post(
            "/manage/users/action/",
            {"user_id": self.user.id, "action": "toggle_active"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.isDelete)

        # 异常：不能停用当前管理员
        response = admin.post(
            "/manage/users/action/",
            {"user_id": self.admin.id, "action": "toggle_active"},
        )
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.isDelete)

        # 异常：非法角色
        response = admin.post(
            "/manage/users/action/",
            {"user_id": self.rider.id, "action": "change_role", "role": "9"},
        )
        self.rider.refresh_from_db()
        self.assertEqual(self.rider.usertype, 1)

        # 主流程：合法改角色
        response = admin.post(
            "/manage/users/action/",
            {"user_id": self.rider.id, "action": "change_role", "role": "0"},
        )
        self.rider.refresh_from_db()
        self.assertEqual(self.rider.usertype, 0)

        # 异常：用户不存在
        response = admin.post(
            "/manage/users/action/", {"user_id": 999999, "action": "toggle_active"}
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_order_actions(self):
        """主流程：标记已送达/异常标记；异常：已评价订单不可改、不支持的操"""
        admin = self.login_as(self.admin)
        order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="后台测试",
            pos=2,
        )
        response = admin.post(
            "/manage/orders/action/", {"order_id": order.id, "action": "complete"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)
        self.assertTrue(order.is_abnormal is False)

        response = admin.post(
            "/manage/orders/action/",
            {"order_id": order.id, "action": "toggle_abnormal"},
        )
        order.refresh_from_db()
        self.assertTrue(order.is_abnormal)

        # 异常：已评价订单（pos=5）不允许管理员修改
        done = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="a",
            pos=5,
        )
        response = admin.post(
            "/manage/orders/action/", {"order_id": done.id, "action": "complete"}
        )
        done.refresh_from_db()
        self.assertEqual(done.pos, 5)

        # 异常：不支持的操作
        response = admin.post(
            "/manage/orders/action/", {"order_id": order.id, "action": "refund"}
        )
        order.refresh_from_db()
        self.assertNotEqual(order.pos, 0)

    def test_admin_blog_and_comment_actions(self):
        """主流程：审核博客/评论（切换逻辑删除）；异常：不存在的内容"""
        admin = self.login_as(self.admin)
        blog = Blog.objects.create(title="待审核", content="内容", authorid=self.user)
        comment = Comment.objects.create(
            blogid=blog, userid=self.user.id, content="评论"
        )

        response = admin.post(
            "/manage/blogs/action/", {"item_type": "blog", "item_id": blog.id}
        )
        self.assertEqual(response.status_code, 302)
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

        response = admin.post(
            "/manage/blogs/action/", {"item_type": "comment", "item_id": comment.id}
        )
        comment.refresh_from_db()
        self.assertTrue(comment.isdeleted)

        response = admin.post(
            "/manage/blogs/action/", {"item_type": "unknown", "item_id": 1}
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_logout(self):
        admin = self.login_as(self.admin)
        response = admin.post("/manage/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")
        response = admin.get("/manage/")
        self.assertEqual(response.status_code, 302)


class CrossModuleIntegrationTest(ApiTestCase):
    """跨模块/跨端集成：订单在用户/骑手/商家端的状态流转与可见性"""

    def test_order_visibility_across_roles(self):
        """主流程：一个订单从下单→接单→备餐→取餐→送达→评价，各端页面同步"""
        user_client = self.login_as(self.user)
        rider_client = self.login_as(self.rider)
        merchant_client = self.login_as(self.merchant)

        # 用户下单（立即下单）
        response = user_client.post(
            f"/foodorder/?foodid={self.food.id}",
            {"num": "1", "address": "跨端地址", "cutlery": "1"},
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=self.user, food=self.food, address="跨端地址")

        # 骑手端看到待接订单
        response = rider_client.get("/rider/")
        self.assertContains(response, self.food.name)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "跨端地址")
        self.assertContains(response, "接单")

        # 骑手接单
        response = rider_client.post(f"/rider_accept/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        self.assertEqual(order.rider, self.rider)

        # 商家端看到待备餐订单
        response = merchant_client.get("/space/")
        self.assertContains(response, self.food.name)
        self.assertContains(response, "完成备餐")

        # 商家备餐
        response = merchant_client.post(f"/merchant_prepare/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)

        # 骑手取餐
        response = rider_client.post(f"/rider_get/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 3)

        # 骑手送达
        response = rider_client.post(f"/rider_deliver/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        # 用户端可评价
        response = user_client.get("/space/")
        self.assertContains(response, "去评价")

        # 用户评价 → 订单完成
        response = user_client.post(
            f"/ordercomment/?orderid={order.id}",
            {"scoretofood": "4.5", "scoretodeliver": "5.0", "comment": "很好吃"},
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.scoretofood), "4.5")
        self.assertEqual(str(order.scoretodeliver), "5.0")

    def test_order_status_endpoint_reflects_state(self):
        """主流程：订单状态页可访问；异常：别人不能操作/非法状态流转被拒绝"""
        user_client = self.login_as(self.user)
        order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="状态测试",
            pos=3,
        )
        response = user_client.get("/orderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "订单状态指示")

        # 异常：骑手送达一个状态不对的订单（pos=3 != 要求？）正例为 pos=3；用非本人骑手试试
        stranger_rider = User.objects.create(
            username="rider2", password="abc12345", phone="13800000017", usertype=1
        )
        other_order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="b",
            pos=3,
            rider=stranger_rider,
        )
        response = self.login_as(self.rider).post(
            f"/rider_deliver/?orderid={other_order.id}"
        )
        self.assertContains(response, "该订单无法操作或不属于您")
        other_order.refresh_from_db()
        self.assertEqual(other_order.pos, 3)

        # 异常：普通用户不能访问骑手专属页
        response = user_client.get("/rider/")
        self.assertContains(response, "只有骑手可以访问此页面")

    def test_order_state_changes_require_post(self):
        order = Order.objects.create(
            user=self.user,
            food=self.food,
            num=1,
            cost=self.food.price,
            address="方法测试",
            pos=0,
        )
        rider_client = self.login_as(self.rider)
        response = rider_client.get(f"/rider_accept/?orderid={order.id}")
        self.assertEqual(response.status_code, 405)
        order.refresh_from_db()
        self.assertEqual(order.pos, 0)

    def test_merchant_space_revenue_aggregation(self):
        """主流程：商家个人中心统计聚合（销售额/订单数/评价均值）"""
        merchant_client = self.login_as(self.merchant)
        for i in range(2):
            Order.objects.create(
                user=self.user,
                food=self.food,
                num=1,
                cost=self.food.price,
                address="聚合",
                pos=4,
            )
        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        # 模板中渲染商家统计数据（至少包含菜品名与商家名）
        self.assertContains(response, self.merchant.username)
        self.assertContains(response, self.food.name)

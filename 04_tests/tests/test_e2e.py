"""
端到端测试（End-to-End Tests）
==============================
测试对象：从页面/接口入口走完一个完整业务流程。
覆盖要求：覆盖清单中的全部业务场景（用例）。

说明：
- 每个测试用例 = 一条完整业务链路（注册/登录 → 操作 → 结果校验）。
- 通过 Django 测试 Client 模拟浏览器请求（表单提交、页面访问），
  并每步用 ORM / 页面内容断言真实业务状态。
- 外部 AI 服务 mock，不访问真实网络。
"""

import json
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_master.test_settings")

import django

django.setup()

from unittest.mock import patch

from django.core.cache import cache
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


class E2EBase(TestCase):
    """端到端测试基类：提供走真实表单注册/登录的辅助方法"""

    def register_user(
        self, username, password="abc12345", phone="13800000000", usertype="0"
    ):
        """走真实注册接口创建用户，返回该用户的登录态 Client"""
        client = Client()
        response = client.post(
            "/account/register/",
            {
                "username": username,
                "password": password,
                "phone": phone,
                "usertype": usertype,
            },
        )
        assert response.status_code == 302, response.content[:200]
        assert response.url == "/account/login/"
        return client

    def login_user(self, username, password="abc12345", usertype="0"):
        """走真实登录接口，返回登录后的 Client（保持 session）"""
        client = Client()
        response = client.post(
            "/account/login/",
            {"username": username, "password": password, "usertype": usertype},
        )
        assert response.status_code == 302, response.content[:200]
        return client

    def login_existing(self, user):
        client = Client()
        session = client.session
        session["user_id"] = user.id
        session.save()
        return client

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


class AccountRegistrationE2ETest(E2EBase):
    """[E2E-TC01 / UC01] 建立账号并进入角色工作台（主流程 + 备选/异常流程）"""

    def test_uc01_main_flow(self):
        """主成功流程：注册三类角色→登录→进入匹配工作台→退出会话失效"""
        # 1. 游客注册普通用户
        self.register_user("uc01_user", phone="13800000201", usertype="0")
        user = User.objects.get(username="uc01_user")
        self.assertEqual(user.usertype, 0)
        self.assertFalse(user.isDelete)
        self.assertEqual(user.phone, "13800000201")

        # 2. 游客注册骑手、商家
        self.register_user("uc01_rider", phone="13800000202", usertype="1")
        self.register_user("uc01_merchant", phone="13800000203", usertype="2")
        self.assertEqual(User.objects.get(username="uc01_rider").usertype, 1)
        self.assertEqual(User.objects.get(username="uc01_merchant").usertype, 2)

        # 3. 登录后进入与角色匹配的工作台
        response = self.login_user("uc01_user", usertype="0").get("/food/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "美食中心")

        response = self.login_user("uc01_rider", usertype="1").get("/rider/")
        self.assertEqual(response.status_code, 200)

        response = self.login_user("uc01_merchant", usertype="2").get("/food/")
        self.assertEqual(response.status_code, 200)

        # 管理员为系统预置账号（不可注册），登录后进入管理后台
        admin = User.objects.create(
            username="uc01_admin", password="abc12345", phone="13800000204", usertype=3
        )
        response = self.login_user("uc01_admin", usertype="3").get("/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, admin.username)

        # 4. 退出后会话被清除，旧会话不可继续使用
        user_client = self.login_user("uc01_user", usertype="0")
        response = user_client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")
        response = user_client.get("/food/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")

    def test_uc01_abnormal_branches(self):
        """备选/异常流程：非法注册被拒、非法登录被拒、游客访问受限页被拒"""
        import re as _re

        # 注册异常：用户名重复
        self.register_user("uc01_dup", phone="13800000205", usertype="0")
        response = Client().post(
            "/account/register/",
            {
                "username": "uc01_dup",
                "password": "abc12345",
                "phone": "13800000206",
                "usertype": "0",
            },
        )
        self.assertContains(response, "用户名已被注册")
        self.assertEqual(User.objects.filter(username="uc01_dup").count(), 1)

        # 注册异常：弱密码 / 手机号错误 / 角色非法 / 禁止注册管理员
        cases = [
            (
                {
                    "username": "u_weak1",
                    "password": "12345678",
                    "phone": "13800000207",
                    "usertype": "0",
                },
                "密码必须在8-16位之间",
            ),
            (
                {
                    "username": "u_badphone",
                    "password": "abc12345",
                    "phone": "123",
                    "usertype": "0",
                },
                "手机号必须是11位数字",
            ),
            (
                {
                    "username": "u_badrole",
                    "password": "abc12345",
                    "phone": "13800000208",
                    "usertype": "9",
                },
                "用户类型只能为普通用户、骑手或商家",
            ),
            (
                {
                    "username": "u_hackadmin",
                    "password": "abc12345",
                    "phone": "13800000209",
                    "usertype": "3",
                },
                "用户类型只能为普通用户、骑手或商家",
            ),
        ]
        for payload, expect in cases:
            with self.subTest(username=payload["username"]):
                response = Client().post("/account/register/", payload)
                self.assertContains(response, expect)
        self.assertFalse(
            User.objects.filter(username__in=["u_hackadmin", "u_badrole"]).exists()
        )

        # 登录异常：用户不存在 / 密码错误 / 身份不匹配 / 账号停用
        response = Client().post(
            "/account/login/",
            {"username": "ghost_user", "password": "abc12345", "usertype": "0"},
        )
        self.assertContains(response, "用户未注册")

        response = Client().post(
            "/account/login/",
            {"username": "uc01_dup", "password": "wrong12345", "usertype": "0"},
        )
        self.assertContains(response, "用户名或者密码错误")

        response = Client().post(
            "/account/login/",
            {"username": "uc01_dup", "password": "abc12345", "usertype": "1"},
        )
        self.assertContains(response, "用户的身份选择错误")

        disabled = User.objects.create(
            username="uc01_disabled",
            password="abc12345",
            phone="13800000210",
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

        # 游客直接访问受限页面被重定向
        for path in ("/food/", "/space/", "/rider/", "/foodsend/", "/manage/"):
            with self.subTest(path=path):
                response = Client().get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn(response.url, ("/index/", "/account/login/"))

        # 会话有效性：非法身份登录不产生会话
        client = Client()
        client.post(
            "/account/login/",
            {"username": "uc01_dup", "password": "wrong12345", "usertype": "0"},
        )
        self.assertNotIn("user_id", client.session)


class FoodDeliveryE2ETest(E2EBase):
    """[E2E-TC02 / UC02] 完成外卖下单、配送履约与评价（主流程 + 备选/异常流程）"""

    def test_full_food_delivery_scenario(self):
        # 1. 从注册入口创建普通用户、骑手、商家
        self.register_user("e2e_user", phone="13800000101", usertype="0")
        self.register_user("e2e_rider", phone="13800000102", usertype="1")
        self.register_user("e2e_merchant", phone="13800000103", usertype="2")
        user = User.objects.get(username="e2e_user")
        rider = User.objects.get(username="e2e_rider")
        merchant = User.objects.get(username="e2e_merchant")

        # 2. 商家从真实新增入口上架菜品（含图片上传）
        merchant_client = self.login_user("e2e_merchant", usertype="2")
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        import tempfile, shutil

        temp_dir = tempfile.mkdtemp()
        try:
            with override_settings(BASE_DIR=temp_dir):
                response = merchant_client.post(
                    "/foodsend/",
                    {
                        "name": "E2E招牌盖饭",
                        "price": "20",
                        "providor": "E2E商家",
                        "inf": "端到端测试菜品",
                        "image": SimpleUploadedFile(
                            "food.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"
                        ),
                    },
                )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        self.assertEqual(response.status_code, 302)
        food = Food.objects.get(name="E2E招牌盖饭", merchant=merchant)
        self.assertTrue(food.image.startswith("images/food/"))

        # 3. 普通用户从页面入口：登录 → 搜索 → 详情 → 立即下单
        user_client = self.login_user("e2e_user", usertype="0")
        response = user_client.get("/food/", {"q": "E2E"})
        payload = self.json_payload(response, "foods-data")
        self.assertIn("E2E招牌盖饭", [f["name"] for f in payload])

        response = user_client.get("/fooddetails/", {"foodid": food.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, food.name)

        response = user_client.post(
            f"/foodorder/?foodid={food.id}",
            {"num": "2", "address": "E2E 大学宿舍", "cutlery": "1"},
        )
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=user, food=food)
        self.assertEqual(order.cost, 40.0)
        self.assertEqual(order.pos, 0)

        # 4. 骑手从页面入口接单 → 商家备餐 → 骑手取餐/送达
        rider_client = self.login_user("e2e_rider", usertype="1")
        response = rider_client.get("/rider/")
        self.assertContains(response, food.name)
        self.assertContains(response, "E2E 大学宿舍")
        self.assertContains(response, "接单")

        response = rider_client.post(f"/rider_accept/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        self.assertEqual(order.rider, rider)

        response = merchant_client.post(f"/merchant_prepare/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)

        response = rider_client.post(f"/rider_get/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 3)

        response = rider_client.get("/space/")
        self.assertContains(response, "配送中")

        response = rider_client.post(f"/rider_deliver/?orderid={order.id}")
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        # 5. 用户评价，链路闭环
        response = user_client.get("/space/")
        self.assertContains(response, "去评价")

        response = user_client.post(
            f"/ordercomment/?orderid={order.id}",
            {
                "scoretofood": "5.0",
                "scoretodeliver": "4.5",
                "comment": "E2E 全流程完成",
            },
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.scoretofood), "5.0")
        self.assertEqual(str(order.scoretodeliver), "4.5")

        # 6. 商家空间能看到已完成订单与统计
        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, food.name)

    def test_uc02_abnormal_branches(self):
        """异常流程：不可售/信息缺失拒单、越权/错误状态推进失败、非法评分与超长评价被拒"""
        self.register_user("uc02_u", phone="13800000401", usertype="0")
        self.register_user("uc02_r", phone="13800000402", usertype="1")
        self.register_user("uc02_r2", phone="13800000403", usertype="1")
        self.register_user("uc02_m", phone="13800000404", usertype="2")
        user_client = self.login_user("uc02_u", usertype="0")
        rider_client = self.login_user("uc02_r", usertype="1")
        rider2_client = self.login_user("uc02_r2", usertype="1")
        merchant_user = User.objects.get(username="uc02_m")
        merchant_client = self.login_user("uc02_m", usertype="2")

        # 售罄/下架菜品拒绝下单
        sold = Food.objects.create(
            name="售罄菜",
            price=10,
            image="x",
            providor="p",
            merchant=merchant_user,
            is_sold_out=True,
        )
        response = user_client.post(
            f"/foodorder/?foodid={sold.id}",
            {"num": "1", "address": "a", "cutlery": "1"},
        )
        self.assertContains(response, "该商品已售罄")

        # 信息不完整拒绝下单
        ok_food = Food.objects.create(
            name="正常菜", price=12, image="x", providor="p", merchant=merchant_user
        )
        response = user_client.post(
            f"/foodorder/?foodid={ok_food.id}", {"num": "1", "cutlery": "1"}
        )
        self.assertContains(response, "请填写完整的下单信息")

        # 正常下单后：订单已被接走 → 其他骑手接单失败
        user_client.post(
            f"/foodorder/?foodid={ok_food.id}",
            {"num": "1", "address": "异常分支地址", "cutlery": "1"},
        )
        order = Order.objects.get(
            user=User.objects.get(username="uc02_u"), food=ok_food
        )
        rider_client.post(f"/rider_accept/?orderid={order.id}")
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        response = rider2_client.post(f"/rider_accept/?orderid={order.id}")
        self.assertContains(response, "该订单已被其他骑手接走或不存在")

        # 非所属商家不能备餐
        stranger = User.objects.create(
            username="uc02_mx", password="abc12345", phone="13800000405", usertype=2
        )
        response = self.login_existing(stranger).post(
            f"/merchant_prepare/?orderid={order.id}"
        )
        self.assertContains(response, "该订单无法操作或不属于您的商品")
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)

        # 非绑定骑手不能取餐/送达
        merchant_client.post(f"/merchant_prepare/?orderid={order.id}")
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)
        response = rider2_client.post(f"/rider_get/?orderid={order.id}")
        self.assertContains(response, "该订单无法操作或不属于您")
        order.refresh_from_db()
        self.assertEqual(order.pos, 2)
        rider_client.post(f"/rider_get/?orderid={order.id}")
        rider_client.post(f"/rider_deliver/?orderid={order.id}")
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        # 非法评分（0/5.5/非数值）与超长评价被拒绝，订单状态不变
        for payload, expect in [
            (
                {"scoretofood": "0", "scoretodeliver": "5.0", "comment": "c"},
                "评分必须大于0.0",
            ),
            (
                {"scoretofood": "5.5", "scoretodeliver": "5.0", "comment": "c"},
                "评分必须大于0.0",
            ),
            (
                {"scoretofood": "abc", "scoretodeliver": "5.0", "comment": "c"},
                "评分必须是数值",
            ),
            (
                {"scoretofood": "4.0", "scoretodeliver": "5.0", "comment": "评" * 201},
                "不能超过200个字符",
            ),
        ]:
            with self.subTest(comment_len=len(payload["comment"])):
                response = user_client.post(
                    f"/ordercomment/?orderid={order.id}", payload
                )
                self.assertContains(response, expect)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)


class CartToOrderE2ETest(E2EBase):
    """[E2E-TC02 / UC02 备选流程] 购物车完整链路（加入 → 更新 → 清空下单 → 配送）"""

    def test_full_cart_scenario(self):
        self.register_user("cart_user", phone="13800000104", usertype="0")
        self.register_user("cart_rider", phone="13800000105", usertype="1")
        self.register_user("cart_merchant", phone="13800000106", usertype="2")
        user = User.objects.get(username="cart_user")
        rider = User.objects.get(username="cart_rider")
        merchant = User.objects.get(username="cart_merchant")
        food = Food.objects.create(
            name="购物车套餐",
            price=15.0,
            image="images/food/1.jpg",
            providor="商家",
            merchant=merchant,
        )

        user_client = self.login_user("cart_user", usertype="0")
        rider_client = self.login_user("cart_rider", usertype="1")
        merchant_client = self.login_user("cart_merchant", usertype="2")

        # 1. 加入购物车（走真实下单表单）
        response = user_client.post(
            f"/foodorder/?foodid={food.id}",
            {"num": "1", "address": "购物车地址", "cutlery": "2"},
        )
        self.assertEqual(response.status_code, 302)
        temp = Temp.objects.get(user=user, food=food)
        self.assertEqual(temp.num, 1)

        # 2. 更新购物车数量（走真实购物车 API）
        response = user_client.post(
            f"/cart/update/{temp.id}/",
            data=json.dumps({"num": "3"}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["num"], 3)

        # 3. 清空购物车 → 生成订单
        response = user_client.post("/cart/clear/")
        self.assertEqual(response.json()["status"], "ok")
        self.assertFalse(Temp.objects.filter(user=user).exists())
        order = Order.objects.get(user=user, food=food)
        self.assertEqual(order.num, 3)
        self.assertEqual(order.cost, 45.0)
        self.assertEqual(order.pos, 0)

        # 4. 走完整配送链路
        rider_client.post(f"/rider_accept/?orderid={order.id}")
        order.refresh_from_db()
        self.assertEqual(order.pos, 1)
        merchant_client.post(f"/merchant_prepare/?orderid={order.id}")
        rider_client.post(f"/rider_get/?orderid={order.id}")
        rider_client.post(f"/rider_deliver/?orderid={order.id}")
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)


class GroupBuyE2ETest(E2EBase):
    """[E2E-TC03 / UC03] 购买并核销到店团购券（主流程 + 备选/异常流程）"""

    def test_full_group_buy_scenario(self):
        self.register_user("gb_user", phone="13800000107", usertype="0")
        self.register_user("gb_merchant", phone="13800000108", usertype="2")
        user = User.objects.get(username="gb_user")
        merchant = User.objects.get(username="gb_merchant")
        food = Food.objects.create(
            name="团购烤鱼",
            price=58.0,
            image="images/food/2.jpg",
            providor="团购商家",
            merchant=merchant,
        )

        user_client = self.login_user("gb_user", usertype="0")
        merchant_client = self.login_user("gb_merchant", usertype="2")

        # 1. 从详情页进入团购下单
        response = user_client.get(f"/groupbuyorder/?foodid={food.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "到店团购下单")

        response = user_client.post(f"/groupbuyorder/?foodid={food.id}", {"num": "3"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "团购券生成成功")
        coupon = GroupBuyCoupon.objects.get(user=user, food=food)
        self.assertEqual(coupon.num, 3)
        self.assertEqual(coupon.cost, 174.0)
        self.assertEqual(coupon.status, 0)

        # 2. 用户空间看到团购券，商家空间看到待核销券
        response = user_client.get("/space/")
        self.assertContains(response, "我的团购券")
        self.assertContains(response, coupon.code)
        self.assertContains(response, "待使用")

        response = merchant_client.get("/space/")
        self.assertContains(response, "团购券核销")
        self.assertContains(response, coupon.code)
        self.assertContains(response, user.username)

        # 3. 商家核销
        response = merchant_client.post("/groupbuy/redeem/", {"code": coupon.code})
        self.assertEqual(response.status_code, 302)
        coupon.refresh_from_db()
        self.assertEqual(coupon.status, 1)
        self.assertIsNotNone(coupon.used_at)

        # 4. 用户空间状态更新
        response = user_client.get("/space/")
        self.assertContains(response, "已使用")

    def test_uc03_abnormal_branches(self):
        """异常流程：非法数量、非商家核销、空码/不存在/他人券、重复核销、已取消券"""
        self.register_user("uc03_u", phone="13800000501", usertype="0")
        self.register_user("uc03_m", phone="13800000502", usertype="2")
        user_client = self.login_user("uc03_u", usertype="0")
        merchant_client = self.login_user("uc03_m", usertype="2")
        merchant = User.objects.get(username="uc03_m")
        food = Food.objects.create(
            name="UC03异常菜", price=30.0, image="x", providor="p", merchant=merchant
        )

        # 数量为空/0/负数/非整数均拒绝
        for bad in (None, "0", "-1", "abc"):
            data = {"num": bad} if bad is not None else {}
            with self.subTest(bad=bad):
                response = user_client.post(f"/groupbuyorder/?foodid={food.id}", data)
                self.assertContains(response, "团购数量")
        self.assertFalse(
            GroupBuyCoupon.objects.filter(
                user=User.objects.get(username="uc03_u"), food=food
            ).exists()
        )

        # 非商家不能核销
        response = user_client.post("/groupbuy/redeem/", {"code": "AAAA111111"})
        self.assertContains(response, "只有商家可以核销团购券")

        # 空核销码
        response = merchant_client.post("/groupbuy/redeem/", {"code": ""})
        self.assertContains(response, "请输入核销码")

        # 正常创建并核销后重复核销被拒绝
        user_client.post(f"/groupbuyorder/?foodid={food.id}", {"num": "2"})
        coupon = GroupBuyCoupon.objects.get(
            user=User.objects.get(username="uc03_u"), food=food
        )
        response = merchant_client.post("/groupbuy/redeem/", {"code": coupon.code})
        self.assertEqual(response.status_code, 302)
        response = merchant_client.post("/groupbuy/redeem/", {"code": coupon.code})
        self.assertContains(response, "该团购券已核销")

        # 不属于自己商品的券不能核销
        other = User.objects.create(
            username="uc03_m2", password="abc12345", phone="13800000503", usertype=2
        )
        other_food = Food.objects.create(
            name="别家菜", price=10, image="x", providor="p", merchant=other
        )
        other_coup = GroupBuyCoupon.objects.create(
            user=User.objects.get(username="uc03_u"),
            food=other_food,
            num=1,
            cost=10,
            code="OTHER2024",
        )
        response = merchant_client.post("/groupbuy/redeem/", {"code": other_coup.code})
        self.assertContains(response, "核销码不存在或不属于您的商品")

        # 已取消的券不能核销
        cancelled = GroupBuyCoupon.objects.create(
            user=User.objects.get(username="uc03_u"),
            food=food,
            num=1,
            cost=30,
            code="CANCEL2024",
            status=2,
        )
        response = merchant_client.post("/groupbuy/redeem/", {"code": cancelled.code})
        self.assertContains(response, "该团购券已取消")


class HotelE2ETest(E2EBase):
    """[E2E-TC04 / UC04] 预订酒店并评价入住体验（主流程 + 备选/异常流程）"""

    def test_full_hotel_scenario(self):
        self.register_user("hotel_user", phone="13800000109", usertype="0")
        self.register_user("hotel_merchant", phone="13800000110", usertype="2")
        merchant = User.objects.get(username="hotel_merchant")
        hotel = Hotel.objects.create(
            name="E2E大酒店",
            addr="中心大道1号",
            price_clock=40,
            price_day=200,
            image="images/hotel/3.jpg",
            inf="高端酒店",
            merchant=merchant,
        )

        user_client = self.login_user("hotel_user", usertype="0")

        # 1. 搜索→详情→预订
        response = user_client.get("/hotel/", {"q": "E2E"})
        hotel_payload = self.json_payload(response, "hotels-data")
        self.assertIn(hotel.name, [h["name"] for h in hotel_payload])
        response = user_client.get("/hoteldetails/", {"hotelid": hotel.id})
        self.assertContains(response, hotel.name)

        response = user_client.post(
            f"/hotelorder/?hotelid={hotel.id}",
            {
                "room_type": "single_day",
                "duration": "2",
                "checkin_time": "2026-07-01T14:00",
            },
        )
        self.assertEqual(response.status_code, 302)
        order = HotelOrder.objects.get(
            user=User.objects.get(username="hotel_user"), hotel=hotel
        )
        self.assertEqual(order.cost, 400.0)
        self.assertEqual(order.pos, 4)
        hotel.refresh_from_db()
        self.assertEqual(hotel.orders, 1)

        # 2. 订单状态页
        response = user_client.get("/hotelorderpos/", {"orderid": order.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "待评价")

        # 3. 评价并校验评分聚合
        response = user_client.post(
            f"/hotelcomment/?orderid={order.id}", {"score": "4.0", "comment": "满意"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        hotel.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(hotel.rating), "4.0")
        self.assertEqual(hotel.ratenum, 1)

    def test_uc04_abnormal_branches(self):
        """异常流程：房型/时长/时间非法拒订、非本人查看与评价被拒、非法评分与超长评价被拒"""
        self.register_user("uc04_u", phone="13800000601", usertype="0")
        self.register_user("uc04_other", phone="13800000602", usertype="0")
        user_client = self.login_user("uc04_u", usertype="0")
        other_client = self.login_user("uc04_other", usertype="0")
        hotel = Hotel.objects.create(
            name="UC04异常酒店",
            addr="a",
            price_day=200,
            price_clock=40,
            image="x",
            inf="i",
        )

        # 未知房型
        response = user_client.post(
            f"/hotelorder/?hotelid={hotel.id}",
            {"room_type": "vip", "duration": "1", "checkin_time": "2026-08-26T10:00"},
        )
        self.assertContains(response, "所选房型不存在")

        # 时长非法（0/负数/非整数）
        for bad in ("0", "-1", "abc"):
            with self.subTest(bad=bad):
                response = user_client.post(
                    f"/hotelorder/?hotelid={hotel.id}",
                    {
                        "room_type": "single_day",
                        "duration": bad,
                        "checkin_time": "2026-08-26T10:00",
                    },
                )
                self.assertIn("入住时间长度", response.content.decode())

        # 入住时间格式非法
        response = user_client.post(
            f"/hotelorder/?hotelid={hotel.id}",
            {"room_type": "single_day", "duration": "1", "checkin_time": "not-time"},
        )
        self.assertContains(response, "入住时间格式不正确")

        # 信息不完整 / 酒店不存在
        response = user_client.post(
            f"/hotelorder/?hotelid={hotel.id}", {"room_type": "single_day"}
        )
        self.assertContains(response, "请填写完整的订房信息")
        response = user_client.post(
            f"/hotelorder/?hotelid=999999",
            {
                "room_type": "single_day",
                "duration": "1",
                "checkin_time": "2026-08-26T10:00",
            },
        )
        self.assertContains(response, "酒店不存在")

        # 正常下单 → 非本人查看/评价被拒
        user_client.post(
            f"/hotelorder/?hotelid={hotel.id}",
            {
                "room_type": "single_day",
                "duration": "1",
                "checkin_time": "2026-08-26T10:00",
            },
        )
        order = HotelOrder.objects.get(
            user=User.objects.get(username="uc04_u"), hotel=hotel
        )
        response = other_client.get("/hotelorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单")
        response = other_client.post(
            f"/hotelcomment/?orderid={order.id}", {"score": "4.0", "comment": "x"}
        )
        self.assertContains(response, "无权评价该订单")

        # 非法评分/超长评价被拒，订单状态不变
        for score, comment, expect in [
            ("0", "c", "评分必须大于0.0"),
            ("5.5", "c", "评分必须大于0.0"),
            ("abc", "c", "评分必须是数值"),
            ("4.0", "评" * 201, "不能超过200个字符"),
        ]:
            with self.subTest(score=score):
                response = user_client.post(
                    f"/hotelcomment/?orderid={order.id}",
                    {"score": score, "comment": comment},
                )
                self.assertContains(response, expect)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)


class PlayE2ETest(E2EBase):
    """[E2E-TC05 / UC05] 购买娱乐门票并评价体验（主流程 + 备选/异常流程）"""

    def test_full_play_scenario(self):
        self.register_user("play_user", phone="13800000111", usertype="0")
        self.register_user("play_merchant", phone="13800000112", usertype="2")
        merchant = User.objects.get(username="play_merchant")
        play = Play.objects.create(
            name="E2E游乐园",
            addr="欢乐街9号",
            price=99.0,
            start_time="09:00",
            open_time="10h",
            image="images/play/5.png",
            inf="大型游乐园",
            merchant=merchant,
        )

        user_client = self.login_user("play_user", usertype="0")

        response = user_client.get("/play/", {"q": "E2E"})
        play_payload = self.json_payload(response, "plays-data")
        self.assertIn(play.name, [p["name"] for p in play_payload])
        response = user_client.get("/playdetails/", {"playid": play.id})
        self.assertContains(response, play.name)

        response = user_client.post(
            f"/playorder/?playid={play.id}",
            {"num": "2", "visit_time": "2026-07-02T09:00"},
        )
        self.assertEqual(response.status_code, 302)
        order = PlayOrder.objects.get(
            user=User.objects.get(username="play_user"), play=play
        )
        self.assertEqual(order.cost, 198.0)
        self.assertEqual(order.pos, 4)

        response = user_client.get("/playorderpos/", {"orderid": order.id})
        self.assertContains(response, "待评价")

        response = user_client.post(
            f"/playcomment/?orderid={order.id}", {"score": "5.0", "comment": "超赞"}
        )
        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        play.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(play.rating), "5.0")
        self.assertEqual(play.ratenum, 1)

    def test_uc05_abnormal_branches(self):
        """异常流程：票数/时间非法拒购、场所不存在、非本人查看与评价被拒、非法评分被拒"""
        self.register_user("uc05_u", phone="13800000701", usertype="0")
        self.register_user("uc05_other", phone="13800000702", usertype="0")
        user_client = self.login_user("uc05_u", usertype="0")
        other_client = self.login_user("uc05_other", usertype="0")
        play = Play.objects.create(
            name="UC05异常乐园", addr="a", price=88, image="x", inf="i"
        )

        # 票数非法
        for bad in ("0", "-1", "abc"):
            with self.subTest(bad=bad):
                response = user_client.post(
                    f"/playorder/?playid={play.id}",
                    {"num": bad, "visit_time": "2026-08-26T09:00"},
                )
                self.assertIn("票数", response.content.decode())

        # 游玩时间格式非法 / 信息不完整
        response = user_client.post(
            f"/playorder/?playid={play.id}", {"num": "1", "visit_time": "bad"}
        )
        self.assertContains(response, "预定时间格式不正确")
        response = user_client.post(f"/playorder/?playid={play.id}", {"num": "1"})
        self.assertContains(response, "请填写完整的购票信息")

        # 场所不存在
        response = user_client.post(
            f"/playorder/?playid=999999", {"num": "1", "visit_time": "2026-08-26T09:00"}
        )
        self.assertContains(response, "娱乐场所不存在")

        # 正常购票 → 非本人查看/评价被拒
        user_client.post(
            f"/playorder/?playid={play.id}",
            {"num": "2", "visit_time": "2026-08-26T09:00"},
        )
        order = PlayOrder.objects.get(
            user=User.objects.get(username="uc05_u"), play=play
        )
        response = other_client.get("/playorderpos/", {"orderid": order.id})
        self.assertContains(response, "无权查看该订单")
        response = other_client.post(
            f"/playcomment/?orderid={order.id}", {"score": "5.0", "comment": "x"}
        )
        self.assertContains(response, "无权评价该订单")

        # 非法评分/超长评价被拒
        for score, comment, expect in [
            ("0", "c", "评分必须大于0.0"),
            ("abc", "c", "评分必须是数值"),
            ("4.0", "评" * 201, "不能超过200个字符"),
        ]:
            with self.subTest(score=score):
                response = user_client.post(
                    f"/playcomment/?orderid={order.id}",
                    {"score": score, "comment": comment},
                )
                self.assertContains(response, expect)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)


class MerchantSupplyE2ETest(E2EBase):
    """[E2E-TC06 / UC06] 发布并维护商家服务供给（主流程 + 备选/异常流程）"""

    def _png(self, name="supply.png", size=64):
        from django.core.files.uploadedfile import SimpleUploadedFile

        return SimpleUploadedFile(
            name, b"\x89PNG\r\n\x1a\n" + b"x" * size, content_type="image/png"
        )

    def _upload_ctx(self):
        import tempfile

        from django.test import override_settings

        ctx = override_settings(BASE_DIR=tempfile.mkdtemp())
        return ctx

    def test_uc06_main_flow(self):
        """主成功流程：商家发布美食/酒店/娱乐 → 列表与空间可见 → 维护菜品状态并同步用户侧"""
        import shutil
        import tempfile

        from django.test import override_settings

        self.register_user("uc06_merchant", phone="13800000301", usertype="2")
        self.register_user("uc06_user", phone="13800000302", usertype="0")
        merchant = User.objects.get(username="uc06_merchant")
        user_client = self.login_user("uc06_user", usertype="0")
        merchant_client = self.login_user("uc06_merchant", usertype="2")

        temp_dir = tempfile.mkdtemp()
        try:
            with override_settings(BASE_DIR=temp_dir):
                # 发布美食
                response = merchant_client.post(
                    "/foodsend/",
                    {
                        "name": "UC06招牌菜",
                        "price": "22.5",
                        "providor": "UC06商家",
                        "inf": "商家发布的美食",
                        "image": self._png("food.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                food = Food.objects.get(name="UC06招牌菜", merchant=merchant)
                self.assertEqual(food.price, 22.5)
                self.assertTrue(food.image.startswith("images/food/"))

                # 发布酒店
                response = merchant_client.post(
                    "/hotelsend/",
                    {
                        "name": "UC06酒店",
                        "addr": "UC06大道8号",
                        "inf": "商家发布的酒店",
                        "price_clock": "40",
                        "price_day": "198",
                        "price_double_clock": "60",
                        "price_double_day": "268",
                        "price_special": "328",
                        "image": self._png("hotel.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                hotel = Hotel.objects.get(name="UC06酒店", merchant=merchant)
                self.assertEqual(hotel.price_day, 198)
                self.assertTrue(hotel.image.startswith("images/hotel/"))

                # 发布娱乐场所
                response = merchant_client.post(
                    "/playsend/",
                    {
                        "name": "UC06乐园",
                        "addr": "UC06欢乐街",
                        "price": "66",
                        "start_time": "10:30",
                        "open_time": "8h",
                        "inf": "商家发布的娱乐场所",
                        "image": self._png("play.png"),
                    },
                )
                self.assertEqual(response.status_code, 302)
                play = Play.objects.get(name="UC06乐园", merchant=merchant)
                self.assertEqual(play.price, 66)
                self.assertEqual(play.start_time, "10:30")
                self.assertTrue(play.image.startswith("images/play/"))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # 新供给在对应列表可见（用户侧）
        payload = self.json_payload(user_client.get("/food/"), "foods-data")
        self.assertIn(food.name, [f["name"] for f in payload])
        payload = self.json_payload(user_client.get("/hotel/"), "hotels-data")
        self.assertIn(hotel.name, [h["name"] for h in payload])
        payload = self.json_payload(user_client.get("/play/"), "plays-data")
        self.assertIn(play.name, [p["name"] for p in payload])

        # 商家个人中心可见
        response = merchant_client.get("/space/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, food.name)

        # 维护菜品状态：售罄 → 用户侧不能下单；恢复后可以；下架 → 用户侧不可见
        response = merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_sold_out"}
        )
        self.assertEqual(response.status_code, 302)
        food.refresh_from_db()
        self.assertTrue(food.is_sold_out)
        response = user_client.post(
            f"/foodorder/?foodid={food.id}",
            {"num": "1", "address": "a", "cutlery": "1"},
        )
        self.assertContains(response, "该商品已售罄")

        merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_sold_out"}
        )
        food.refresh_from_db()
        self.assertFalse(food.is_sold_out)

        merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_off_shelf"}
        )
        food.refresh_from_db()
        self.assertTrue(food.is_off_shelf)
        payload = self.json_payload(user_client.get("/food/"), "foods-data")
        self.assertNotIn(food.name, [f["name"] for f in payload])
        response = user_client.get("/fooddetails/", {"foodid": food.id})
        self.assertContains(response, "该商品已下架")

        merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_off_shelf"}
        )
        food.refresh_from_db()
        self.assertFalse(food.is_off_shelf)
        payload = self.json_payload(user_client.get("/food/"), "foods-data")
        self.assertIn(food.name, [f["name"] for f in payload])

        # 购物车包含不可售商品时整体拒绝结算
        user_client.post(
            f"/foodorder/?foodid={food.id}",
            {"num": "1", "address": "购物车", "cutlery": "2"},
        )
        merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_sold_out"}
        )
        response = user_client.post("/cart/clear/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertIn("已下架或售罄", response.json()["msg"])

    def test_uc06_abnormal_branches(self):
        """备选/异常流程：非商家、字段缺失、价格/时间非法、图片非法、越权维护全部被拒"""
        import shutil
        import tempfile

        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings

        self.register_user("uc06_merchant2", phone="13800000303", usertype="2")
        self.register_user("uc06_user2", phone="13800000304", usertype="0")
        self.register_user("uc06_other_merchant", phone="13800000305", usertype="2")
        merchant = User.objects.get(username="uc06_merchant2")
        merchant_client = self.login_user("uc06_merchant2", usertype="2")
        user_client = self.login_user("uc06_user2", usertype="0")
        other_client = self.login_user("uc06_other_merchant", usertype="2")

        # 非商家访问发布页
        for path, expect in [
            ("/foodsend/", "只有商家可以添加美食"),
            ("/hotelsend/", "只有商家可以添加酒店"),
            ("/playsend/", "只有商家可以添加娱乐场所"),
        ]:
            with self.subTest(path=path):
                self.assertContains(user_client.get(path), expect)

        temp_dir = tempfile.mkdtemp()
        try:
            with override_settings(BASE_DIR=temp_dir):
                # 必填字段缺失
                self.assertContains(
                    merchant_client.post("/foodsend/", {"name": "x", "price": "10"}),
                    "请填写完整的美食信息",
                )
                self.assertContains(
                    merchant_client.post("/hotelsend/", {"name": "x"}),
                    "请填写酒店名称、地址和图片路径",
                )
                self.assertContains(
                    merchant_client.post("/playsend/", {"name": "x", "price": "10"}),
                    "请填写完整的娱乐场所信息",
                )

                # 价格非法
                self.assertContains(
                    merchant_client.post(
                        "/foodsend/",
                        {
                            "name": "x",
                            "price": "abc",
                            "providor": "p",
                            "image": self._png("f.png"),
                        },
                    ),
                    "价格必须是数字",
                )
                self.assertContains(
                    merchant_client.post(
                        "/playsend/",
                        {
                            "name": "x",
                            "addr": "a",
                            "price": "abc",
                            "image": self._png("p.png"),
                        },
                    ),
                    "门票价格必须是数字",
                )

                # 营业时间格式非法
                self.assertContains(
                    merchant_client.post(
                        "/playsend/",
                        {
                            "name": "x",
                            "addr": "a",
                            "price": "10",
                            "start_time": "9:00",
                            "image": self._png("p.png"),
                        },
                    ),
                    "开始营业时间格式不正确",
                )
                self.assertContains(
                    merchant_client.post(
                        "/playsend/",
                        {
                            "name": "x",
                            "addr": "a",
                            "price": "10",
                            "start_time": "25:00",
                            "image": self._png("p.png"),
                        },
                    ),
                    "开始营业时间不合法",
                )
                self.assertContains(
                    merchant_client.post(
                        "/playsend/",
                        {
                            "name": "x",
                            "addr": "a",
                            "price": "10",
                            "start_time": "10:00",
                            "open_time": "8",
                            "image": self._png("p.png"),
                        },
                    ),
                    "运营时间格式不正确",
                )

                # 图片缺失 / 类型非法 / 超大
                self.assertContains(
                    merchant_client.post(
                        "/foodsend/", {"name": "x", "price": "10", "providor": "p"}
                    ),
                    "请上传图片",
                )
                bad_type = SimpleUploadedFile(
                    "a.txt", b"abc", content_type="text/plain"
                )
                self.assertContains(
                    merchant_client.post(
                        "/foodsend/",
                        {
                            "name": "x",
                            "price": "10",
                            "providor": "p",
                            "image": bad_type,
                        },
                    ),
                    "只支持 JPG 或 PNG 格式图片",
                )
                too_big = SimpleUploadedFile(
                    "big.png",
                    b"\x89PNG\r\n\x1a\n" + b"x" * (2 * 1024 * 1024),
                    content_type="image/png",
                )
                self.assertContains(
                    merchant_client.post(
                        "/foodsend/",
                        {"name": "x", "price": "10", "providor": "p", "image": too_big},
                    ),
                    "图片大小不能超过 2MB",
                )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        # 越权维护他人菜品 / 不支持的操作
        food = Food.objects.create(
            name="他人菜品", price=10.0, image="x", providor="p", merchant=merchant
        )
        response = other_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "toggle_off_shelf"}
        )
        self.assertContains(response, "商品不存在或不属于当前商家")
        food.refresh_from_db()
        self.assertFalse(food.is_off_shelf)

        response = merchant_client.post(
            "/merchant/food/action/", {"food_id": food.id, "action": "delete"}
        )
        self.assertContains(response, "不支持的商品操作")


class BlogE2ETest(E2EBase):
    """[E2E-TC07 / UC07] 发布内容并参与社区互动（主流程 + 备选/异常流程）"""

    def test_full_blog_scenario(self):
        self.register_user("blog_user", phone="13800000113", usertype="0")
        user = User.objects.get(username="blog_user")
        user_client = self.login_user("blog_user", usertype="0")

        # 发布
        response = user_client.post(
            "/blogsend/", {"title": "E2E 游记", "content": "今天去了游乐园"}
        )
        self.assertEqual(response.status_code, 302)
        blog = Blog.objects.get(authorid=user)
        self.assertFalse(blog.isdeleted)

        # 列表与详情
        response = user_client.get("/blog/", {"q": "游记"})
        self.assertContains(response, blog.title)
        response = user_client.get("/blogsdetails/", {"blogid": blog.id})
        self.assertContains(response, blog.title)

        # AJAX 评论
        response = user_client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "写得真好"}),
            content_type="application/json",
        )
        self.assertEqual(response.json()["status"], "ok")
        comment = Comment.objects.get(blogid=blog)
        self.assertEqual(comment.content, "写得真好")

        # 删除评论 → 删除博客（逻辑删除后列表不可见）
        response = user_client.delete(f"/blogcomment/delete/?commentid={comment.id}")
        self.assertEqual(response.json()["success"], True)
        comment.refresh_from_db()
        self.assertTrue(comment.isdeleted)

        response = user_client.delete(f"/blog/delete/?blogid={blog.id}")
        self.assertEqual(response.json()["success"], True)
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

        response = user_client.get("/blog/", {"q": "游记"})
        self.assertNotContains(response, blog.title)

    def test_uc07_abnormal_branches(self):
        """异常流程：内容为空拒发、评论非法/不存在/未登录、越权删除、删除后不可见"""
        self.register_user("uc07_u", phone="13800000801", usertype="0")
        self.register_user("uc07_other", phone="13800000802", usertype="0")
        user_client = self.login_user("uc07_u", usertype="0")
        other_client = self.login_user("uc07_other", usertype="0")
        user = User.objects.get(username="uc07_u")

        # 标题/正文为空拒绝发布
        response = user_client.post("/blogsend/", {"title": "", "content": ""})
        self.assertContains(response, "标题和内容不能为空")

        # 正常发布
        user_client.post("/blogsend/", {"title": "异常分支博客", "content": "内容"})
        blog = Blog.objects.get(authorid=user)

        # 评论异常：空内容/超长/非法JSON/博客不存在/未登录
        response = user_client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response = user_client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "长" * 501}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response = user_client.post(
            "/blogcomment/", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        response = user_client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": 999999, "content": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        response = Client().post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # 非作者不能删除博客；错误方法被拒
        response = other_client.delete(f"/blog/delete/?blogid={blog.id}")
        self.assertEqual(response.status_code, 404)
        response = user_client.get("/blog/delete/")
        self.assertEqual(response.status_code, 405)

        # 非评论者不能删除评论
        user_client.post(
            "/blogcomment/",
            data=json.dumps({"blog_id": blog.id, "content": "正常评论"}),
            content_type="application/json",
        )
        comment = Comment.objects.get(blogid=blog, isdeleted=False)
        response = other_client.delete(f"/blogcomment/delete/?commentid={comment.id}")
        self.assertEqual(response.status_code, 404)
        comment.refresh_from_db()
        self.assertFalse(comment.isdeleted)

        # 删除后详情与公开列表均不可见
        user_client.delete(f"/blog/delete/?blogid={blog.id}")
        response = user_client.get("/blogsdetails/", {"blogid": blog.id})
        self.assertContains(response, "博客不存在")
        response = user_client.get("/blog/", {"q": "异常分支"})
        self.assertNotContains(response, blog.title)


class AdminE2ETest(E2EBase):
    """[E2E-TC09 / UC09] 开展平台运营治理（主流程 + 备选/异常流程）"""

    def test_full_admin_scenario(self):
        # 准备业务数据
        self.register_user("admin_target_user", phone="13800000114", usertype="0")
        self.register_user("admin_rider", phone="13800000115", usertype="1")
        self.register_user("admin_merchant", phone="13800000116", usertype="2")
        user = User.objects.get(username="admin_target_user")
        merchant = User.objects.get(username="admin_merchant")
        food = Food.objects.create(
            name="后台菜", price=10.0, image="x", providor="p", merchant=merchant
        )
        order = Order.objects.create(
            user=user, food=food, num=1, cost=10.0, address="后台地址", pos=2
        )
        blog = Blog.objects.create(title="后台待审博客", content="内容", authorid=user)
        admin = User.objects.create(
            username="boss_admin", password="abc12345", phone="13800000117", usertype=3
        )

        # 管理员从登录入口进入后台
        admin_client = self.login_user("boss_admin", usertype="3")
        response = admin_client.get("/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, admin.username)

        # 1. 停用违规用户 → 该用户无法再登录
        response = admin_client.post(
            "/manage/users/action/", {"user_id": user.id, "action": "toggle_active"}
        )
        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.isDelete)
        response = Client().post(
            "/account/login/",
            {"username": user.username, "password": "abc12345", "usertype": "0"},
        )
        self.assertContains(response, "该账号已被停用")

        # 2. 订单标记为已送达
        response = admin_client.post(
            "/manage/orders/action/", {"order_id": order.id, "action": "complete"}
        )
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

        # 3. 审核博客（下架）
        response = admin_client.post(
            "/manage/blogs/action/", {"item_type": "blog", "item_id": blog.id}
        )
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)

        # 4. 管理员退出
        response = admin_client.post("/manage/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

    def test_uc09_abnormal_branches(self):
        """异常流程：非管理员被拒、不能停用/降级自己、已评价订单不可改、目标不存在、内容恢复"""
        self.register_user("uc09_u", phone="13800001001", usertype="0")
        self.register_user("uc09_m", phone="13800001002", usertype="2")
        user = User.objects.get(username="uc09_u")
        merchant = User.objects.get(username="uc09_m")
        food = Food.objects.create(
            name="治理菜品", price=10, image="x", providor="p", merchant=merchant
        )
        admin = User.objects.create(
            username="uc09_admin", password="abc12345", phone="13800001003", usertype=3
        )
        admin_client = self.login_user("uc09_admin", usertype="3")

        # 非管理员访问被重定向
        response = self.login_user("uc09_u", usertype="0").get("/manage/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

        # 不能停用自己 / 不能移除自己的管理员角色
        admin_client.post(
            "/manage/users/action/", {"user_id": admin.id, "action": "toggle_active"}
        )
        admin.refresh_from_db()
        self.assertFalse(admin.isDelete)
        admin_client.post(
            "/manage/users/action/",
            {"user_id": admin.id, "action": "change_role", "role": "0"},
        )
        admin.refresh_from_db()
        self.assertEqual(admin.usertype, 3)

        # 已评价订单（pos=5）不能被管理员改写
        done = Order.objects.create(
            user=user, food=food, num=1, cost=10, address="a", pos=5
        )
        admin_client.post(
            "/manage/orders/action/", {"order_id": done.id, "action": "complete"}
        )
        done.refresh_from_db()
        self.assertEqual(done.pos, 5)

        # 异常标记可切换并解除
        order = Order.objects.create(
            user=user, food=food, num=1, cost=10, address="b", pos=2
        )
        admin_client.post(
            "/manage/orders/action/",
            {"order_id": order.id, "action": "toggle_abnormal"},
        )
        order.refresh_from_db()
        self.assertTrue(order.is_abnormal)
        admin_client.post(
            "/manage/orders/action/",
            {"order_id": order.id, "action": "toggle_abnormal"},
        )
        order.refresh_from_db()
        self.assertFalse(order.is_abnormal)

        # 目标不存在时不崩溃
        for path, payload in [
            ("/manage/users/action/", {"user_id": 999999, "action": "toggle_active"}),
            ("/manage/orders/action/", {"order_id": 999999, "action": "complete"}),
            ("/manage/blogs/action/", {"item_type": "blog", "item_id": 999999}),
        ]:
            with self.subTest(path=path):
                response = admin_client.post(path, payload)
                self.assertEqual(response.status_code, 302)

        # 隐藏内容后公开列表不可见，恢复后重新可见
        blog = Blog.objects.create(title="治理博客", content="内容", authorid=user)
        admin_client.post(
            "/manage/blogs/action/", {"item_type": "blog", "item_id": blog.id}
        )
        blog.refresh_from_db()
        self.assertTrue(blog.isdeleted)
        response = self.login_user("uc09_u", usertype="0").get("/blog/", {"q": "治理"})
        self.assertNotContains(response, blog.title)
        admin_client.post(
            "/manage/blogs/action/", {"item_type": "blog", "item_id": blog.id}
        )
        blog.refresh_from_db()
        self.assertFalse(blog.isdeleted)
        response = self.login_user("uc09_u", usertype="0").get("/blog/", {"q": "治理"})
        self.assertContains(response, blog.title)


class AiAssistantE2ETest(E2EBase):
    """[E2E-TC08 / UC08] 获取个性化 AI 咨询（主流程 + 备选/异常流程，外部模型 mock）"""

    def test_full_ai_assistant_scenario(self):
        cache.clear()
        self.register_user("ai_user", phone="13800000118", usertype="0")
        self.register_user("ai_merchant", phone="13800000119", usertype="2")
        merchant = User.objects.get(username="ai_merchant")
        Food.objects.create(
            name="AI推荐菜", price=25.0, image="x", providor="AI商家", merchant=merchant
        )
        Hotel.objects.create(
            name="AI推荐酒店", addr="x", price_day=100, image="y", merchant=merchant
        )
        Play.objects.create(
            name="AI推荐乐园", addr="x", price=50, image="z", merchant=merchant
        )

        user_client = self.login_user("ai_user", usertype="0")
        with patch(
            "myapp.views.call_aliyun_llm", return_value="为您推荐：AI推荐菜"
        ) as mock_call:
            response = user_client.post("/ai-chat/", {"user_input": "今天吃什么"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "为您推荐：AI推荐菜")
        prompt = mock_call.call_args.kwargs["system_prompt"]
        self.assertIn("AI推荐菜", prompt)
        self.assertIn("AI推荐酒店", prompt)
        self.assertIn("AI推荐乐园", prompt)

    def test_uc08_abnormal_branches(self):
        """异常流程：未登录重定向、空输入 400、服务失败 500、下架/售罄不进入上下文"""
        cache.clear()
        self.register_user("uc08_u", phone="13800000901", usertype="0")
        self.register_user("uc08_m", phone="13800000902", usertype="2")
        merchant = User.objects.get(username="uc08_m")
        Food.objects.create(
            name="正常可售菜", price=10, image="x", providor="p", merchant=merchant
        )
        Food.objects.create(
            name="已下架隐藏菜",
            price=10,
            image="x",
            providor="p",
            merchant=merchant,
            is_off_shelf=True,
        )
        Food.objects.create(
            name="已售罄隐藏菜",
            price=10,
            image="x",
            providor="p",
            merchant=merchant,
            is_sold_out=True,
        )

        # 未登录 → 重定向首页
        response = Client().post("/ai-chat/", {"user_input": "推荐"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/index/")

        user_client = self.login_user("uc08_u", usertype="0")

        # 空输入 → 400
        response = user_client.post("/ai-chat/", {"user_input": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "输入不能为空")

        # 外部服务无响应 → 500
        with patch("myapp.views.call_aliyun_llm", return_value=None):
            response = user_client.post("/ai-chat/", {"user_input": "推荐"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("AI 服务暂时不可用", response.json()["error"])

        # 下架/售罄菜品不进入全局上下文（缓存已清空，重新生成）
        with patch("myapp.views.call_aliyun_llm", return_value="ok") as mock_call:
            response = user_client.post("/ai-chat/", {"user_input": "推荐"})
        self.assertEqual(response.status_code, 200)
        prompt = mock_call.call_args.kwargs["system_prompt"]
        self.assertIn("正常可售菜", prompt)
        self.assertNotIn("已下架隐藏菜", prompt)
        self.assertNotIn("已售罄隐藏菜", prompt)

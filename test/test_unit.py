"""
单元测试（Unit Tests）
======================
测试对象：关键类、方法、业务规则和异常分支。
特点：不发起 HTTP 请求，直接调用函数/方法，通过断言（assert）判断结果是否正确。

覆盖内容：
1. 价格/房型映射规则         get_hotel_room_price / ROOM_PRICE_FIELDS / ROOM_TYPE_LABELS
2. 酒店评价业务规则           save_hotel_review / update_hotel_rating（含异常分支）
3. 娱乐评价业务规则           save_play_review / update_play_rating（含异常分支）
4. 团购核销码生成规则         make_group_buy_code（格式 + 唯一性）
5. 角色判断工具函数           is_merchant / is_rider / get_login_user
6. 登录密码强度业务规则       （8-16 位且同时包含字母和数字）
7. 模型字段校验规则           Food.rating / Order.scoretofood 的 0~5 校验
8. 外部 AI 客户端方法         call_aliyun_llm（成功、无 key、网络异常、非 200）
9. 管理员权限装饰器           admin_required（未登录 / 非管理员 / 管理员）

追溯编号映射（详见 追溯表.md）：
- UNIT-TC01：PasswordBusinessRuleTest、UserHelperRuleTest
- UNIT-TC03：GroupBuyCodeRuleTest
- UNIT-TC04：HotelPriceRuleTest、HotelReviewRuleTest
- UNIT-TC05：PlayReviewRuleTest
- UNIT-TC06：ModelValidationRuleTest
- UNIT-TC08：LlmClientTest
- UNIT-TC09：AdminRequiredDecoratorTest
"""
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_master.test_settings")

import django

django.setup()

from unittest.mock import MagicMock, patch

import requests
from django.core.exceptions import ValidationError
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from myapp import admin_views, views, views1
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
from myapp.utils.llm_client import call_aliyun_llm


class HotelPriceRuleTest(TestCase):
    """价格/房型映射规则单元测试"""

    @classmethod
    def setUpTestData(cls):
        cls.hotel = Hotel.objects.create(
            name="测试酒店",
            addr="测试地址",
            price_clock=30.0,
            price_day=180.0,
            price_double_clock=50.0,
            price_double_day=260.0,
            price_special=320.0,
            image="images/hotel/1.jpg",
            inf="测试酒店简介",
        )

    def test_known_room_types_return_corresponding_price(self):
        """主流程：每种合法房型都能取到正确价格"""
        cases = {
            "single_clock": 30.0,
            "single_day": 180.0,
            "double_clock": 50.0,
            "double_day": 260.0,
            "special_day": 320.0,
        }
        for room_type, expected in cases.items():
            with self.subTest(room_type=room_type):
                self.assertEqual(views1.get_hotel_room_price(self.hotel, room_type), expected)

    def test_unknown_room_type_returns_none(self):
        """异常分支：未知房型应返回 None"""
        self.assertIsNone(views1.get_hotel_room_price(self.hotel, "vip_room"))

    def test_none_price_returns_none(self):
        """异常分支：未配置价格的房型（字段为 None）应返回 None"""
        hotel = Hotel.objects.create(
            name="无价格酒店",
            addr="地址",
            price_clock=None,
            price_day=None,
            image="images/hotel/2.jpg",
        )
        self.assertIsNone(views1.get_hotel_room_price(hotel, "single_clock"))
        self.assertIsNone(views1.get_hotel_room_price(hotel, "single_day"))

    def test_room_type_field_mapping_is_consistent(self):
        """业务规则：ROOM_PRICE_FIELDS 与 ROOM_TYPE_LABELS 的键集合应一致"""
        self.assertEqual(
            set(views1.ROOM_PRICE_FIELDS.keys()),
            set(views1.ROOM_TYPE_LABELS.keys()),
        )
        self.assertIn("single_day", views1.ROOM_TYPE_LABELS)
        self.assertEqual(views1.ROOM_TYPE_LABELS["single_day"], "单人间日租")


class HotelReviewRuleTest(TestCase):
    """酒店评价业务规则单元测试（含异常分支）"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="u1", password="abc12345", phone="13800000001", usertype=0)
        cls.hotel = Hotel.objects.create(
            name="酒店A", addr="地址A", price_day=180.0, image="images/hotel/1.jpg"
        )

    def _order(self):
        return HotelOrder.objects.create(
            user=self.user,
            hotel=self.hotel,
            room_type="single_day",
            duration=1,
            checkin_time=timezone.now(),
            cost=180.0,
            pos=4,
        )

    def test_save_hotel_review_success_updates_order_and_hotel(self):
        """主流程：合法评价 → 订单 pos=5、评分保存、酒店评分/人数更新"""
        order = self._order()
        error = views1.save_hotel_review(order, "4.5", "入住体验不错")
        self.assertIsNone(error)
        order.refresh_from_db()
        self.hotel.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.score), "4.5")
        self.assertEqual(order.comment, "入住体验不错")
        self.assertEqual(str(self.hotel.rating), "4.5")
        self.assertEqual(self.hotel.ratenum, 1)
        self.assertEqual(self.hotel.orders, 0)  # 评价不增加订单数

    def test_save_hotel_review_zero_score_rejected(self):
        """异常分支：0 分不允许"""
        order = self._order()
        error = views1.save_hotel_review(order, "0", "评论")
        self.assertIn("评分必须大于0.0", error)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

    def test_save_hotel_review_above_five_rejected(self):
        """异常分支：超过 5 分不允许"""
        order = self._order()
        error = views1.save_hotel_review(order, "5.5", "评论")
        self.assertIn("评分必须大于0.0", error)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

    def test_save_hotel_review_non_numeric_rejected(self):
        """异常分支：非数值评分不允许（TypeError/ValueError）"""
        order = self._order()
        for bad in ("abc", None, "", "4,5"):
            with self.subTest(bad=bad):
                error = views1.save_hotel_review(order, bad, "评论")
                self.assertIn("评分必须是数值", error)

    def test_save_hotel_review_comment_too_long_rejected(self):
        """异常分支：评论超过 200 字符不允许"""
        order = self._order()
        error = views1.save_hotel_review(order, "4.0", "评" * 201)
        self.assertIn("不能超过200个字符", error)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

    def test_save_hotel_review_comment_max_length_accepted(self):
        """边界分支：评论恰好 200 字符允许"""
        order = self._order()
        error = views1.save_hotel_review(order, "4.0", "评" * 200)
        self.assertIsNone(error)
        order.refresh_from_db()
        self.assertEqual(order.pos, 5)

    def test_update_hotel_rating_aggregates_multiple_reviews(self):
        """业务规则：多订单评分取平均并四舍五入到 1 位小数"""
        for score in ("4.0", "5.0"):
            order = self._order()
            views1.save_hotel_review(order, score, "好")
        self.hotel.refresh_from_db()
        self.assertEqual(str(self.hotel.rating), "4.5")
        self.assertEqual(self.hotel.ratenum, 2)

    def test_update_hotel_rating_resets_when_no_reviews(self):
        """业务规则：无有效评价时评分重置为 0"""
        order = self._order()
        views1.save_hotel_review(order, "5.0", "好")
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.ratenum, 1)
        # 模拟评分被清除（无 pos=5 且 score>0 的记录）
        HotelOrder.objects.filter(hotel=self.hotel).update(score=0.0)
        views1.update_hotel_rating(self.hotel)
        self.hotel.refresh_from_db()
        self.assertEqual(str(self.hotel.rating), "0.0")
        self.assertEqual(self.hotel.ratenum, 0)


class PlayReviewRuleTest(TestCase):
    """娱乐评价业务规则单元测试"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="u2", password="abc12345", phone="13800000002", usertype=0)
        cls.play = Play.objects.create(
            name="乐园A", addr="地址B", price=88.0, image="images/play/1.png"
        )

    def _order(self):
        return PlayOrder.objects.create(
            user=self.user,
            play=self.play,
            num=2,
            visit_time=timezone.now(),
            cost=176.0,
            pos=4,
        )

    def test_save_play_review_success(self):
        """主流程：合法评价保存并更新评分"""
        order = self._order()
        error = views1.save_play_review(order, "4.5", "值得去")
        self.assertIsNone(error)
        order.refresh_from_db()
        self.play.refresh_from_db()
        self.assertEqual(order.pos, 5)
        self.assertEqual(str(order.score), "4.5")
        self.assertEqual(str(self.play.rating), "4.5")
        self.assertEqual(self.play.ratenum, 1)

    def test_save_play_review_invalid_scores_rejected(self):
        """异常分支：0/超5/非数值均被拒绝"""
        order = self._order()
        for bad in ("0", "5.1", "abc", None):
            with self.subTest(bad=bad):
                error = views1.save_play_review(order, bad, "评论")
                self.assertIsNotNone(error)
        order.refresh_from_db()
        self.assertEqual(order.pos, 4)

    def test_save_play_review_comment_too_long_rejected(self):
        """异常分支：评论过长被拒绝"""
        order = self._order()
        error = views1.save_play_review(order, "4.0", "评" * 201)
        self.assertIn("不能超过200个字符", error)

    def test_update_play_rating_aggregates(self):
        """业务规则：多订单平均分与人数正确"""
        for score in ("4.0", "5.0"):
            views1.save_play_review(self._order(), score, "好")
        self.play.refresh_from_db()
        self.assertEqual(str(self.play.rating), "4.5")
        self.assertEqual(self.play.ratenum, 2)


class GroupBuyCodeRuleTest(TestCase):
    """团购核销码生成规则单元测试"""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="u3", password="abc12345", phone="13800000003", usertype=0)
        cls.food = Food.objects.create(name="测试菜", price=10.0, image="x", providor="p", merchant=None)

    def test_make_group_buy_code_format(self):
        """主流程：核销码为 10 位大写十六进制字符串"""
        code = views.make_group_buy_code()
        self.assertRegex(code, r"^[0-9A-F]{10}$")
        self.assertEqual(len(code), 10)

    def test_make_group_buy_code_avoids_existing_codes(self):
        """业务规则：遇到已存在的核销码应重新生成（唯一性）"""
        GroupBuyCoupon.objects.create(
            user=self.user, food=self.food, num=1, cost=10.0, code="AAAAAAAAAA"
        )
        # 第一次生成的码与已存在的 AAAAAAAAAA 冲突，第二次才成功
        with patch("myapp.views.uuid.uuid4") as mock_uuid:
            mock_uuid.side_effect = [
                MagicMock(hex="aaaaaaaaaa"),  # 冲突
                MagicMock(hex="bbbbbbbbbb"),  # 不冲突
            ]
            code = views.make_group_buy_code()
        self.assertEqual(code, "BBBBBBBBBB")
        self.assertFalse(GroupBuyCoupon.objects.filter(code=code).exists())

    def test_group_buy_coupon_unique_constraint_enforced(self):
        """业务规则：数据库层核销码唯一约束"""
        GroupBuyCoupon.objects.create(
            user=self.user, food=self.food, num=1, cost=10.0, code="UNIQUE12345"
        )
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            GroupBuyCoupon.objects.create(
                user=self.user, food=self.food, num=1, cost=10.0, code="UNIQUE12345"
            )


class UserHelperRuleTest(TestCase):
    """角色判断与登录用户获取工具函数单元测试"""

    @classmethod
    def setUpTestData(cls):
        cls.normal = User.objects.create(username="n1", password="abc12345", phone="13800000004", usertype=0)
        cls.rider = User.objects.create(username="r1", password="abc12345", phone="13800000005", usertype=1)
        cls.merchant = User.objects.create(username="m1", password="abc12345", phone="13800000006", usertype=2)

    def test_is_merchant_true_only_for_merchant(self):
        self.assertTrue(views.is_merchant(self.merchant))
        self.assertFalse(views.is_merchant(self.normal))
        self.assertFalse(views.is_merchant(self.rider))

    def test_is_merchant_none_user_returns_false(self):
        """异常分支：未登录（None）应返回 False"""
        self.assertFalse(views.is_merchant(None))

    def test_is_rider_true_only_for_rider(self):
        self.assertTrue(views.is_rider(self.rider))
        self.assertFalse(views.is_rider(self.normal))
        self.assertFalse(views.is_rider(self.merchant))
        self.assertFalse(views.is_rider(None))

    def test_get_login_user_from_session(self):
        """主流程：session 有 user_id 时返回对应用户"""
        request = RequestFactory().get("/")
        request.session = {"user_id": self.normal.id}
        self.assertEqual(views.get_login_user(request), self.normal)

    def test_get_login_user_without_session_returns_none(self):
        """异常分支：未登录 / 用户不存在返回 None"""
        request = RequestFactory().get("/")
        request.session = {}
        self.assertIsNone(views.get_login_user(request))

        request.session = {"user_id": 999999}
        self.assertIsNone(views.get_login_user(request))


class PasswordBusinessRuleTest(SimpleTestCase):
    """登录/注册密码强度业务规则（8-16 位且必须同时含字母和数字）"""

    RULE = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d).{8,16}$")

    def test_valid_passwords_match(self):
        for pwd in ("abc12345", "Aa1234567890", "abcd1234abcd", "1a2b3c4d"):
            with self.subTest(pwd=pwd):
                self.assertRegex(pwd, self.RULE)

    def test_invalid_passwords_rejected(self):
        """异常分支：无字母 / 无数字 / 长度越界均不匹配"""
        bad = [
            "12345678",   # 只有数字
            "abcdefgh",   # 只有字母
            "abc123",     # 少于 8 位
            "a1" * 9,     # 18 位（超过 16 位）
            "aaaa12345",  # 长度 9 含字母数字（合法样例，用于对照）
        ]
        for pwd in bad[:-1]:
            with self.subTest(pwd=pwd):
                self.assertIsNone(self.RULE.match(pwd))
        # 对照：合法样例应匹配
        self.assertIsNotNone(self.RULE.match(bad[-1]))


class ModelValidationRuleTest(TestCase):
    """模型字段校验规则单元测试：评分必须位于 0.0~5.0"""

    def test_food_rating_within_range_ok(self):
        food = Food(name="校验菜", price=10.0, image="x", providor="p", inf="简介", rating=4.5)
        food.full_clean()  # 不抛异常即通过

    def test_food_rating_out_of_range_raises(self):
        """异常分支：评分 6.0 / -0.1 触发 ValidationError"""
        for bad in (6.0, -0.1):
            with self.subTest(bad=bad):
                food = Food(name="校验菜2", price=10.0, image="x", providor="p", inf="简介", rating=bad)
                with self.assertRaises(ValidationError):
                    food.full_clean()

    def test_order_score_fields_valid(self):
        user = User.objects.create(username="u4", password="abc12345", phone="13800000007", usertype=0)
        food = Food.objects.create(name="校验菜3", price=1.0, image="x", providor="p", inf="简介")
        order = Order.objects.create(
            user=user, food=food, num=1, cost=1.0, address="a", comment="c",
            scoretofood=4.5, scoretodeliver=4.5,
        )
        order.full_clean()  # 合法值不抛异常

    def test_order_score_fields_out_of_range_raises(self):
        """异常分支：订单评分超界触发 ValidationError"""
        user = User.objects.create(username="u5", password="abc12345", phone="13800000010", usertype=0)
        food = Food.objects.create(name="校验菜4", price=1.0, image="x", providor="p", inf="简介")
        order = Order.objects.create(
            user=user, food=food, num=1, cost=1.0, address="a", comment="c",
            scoretofood=5.5, scoretodeliver=0.0,
        )
        with self.assertRaises(ValidationError):
            order.full_clean()


class LlmClientTest(SimpleTestCase):
    """外部 AI 客户端 call_aliyun_llm 单元测试"""

    def test_no_api_key_returns_none_without_network(self):
        """异常分支：未配置 API Key 直接返回 None，且不发起网络请求"""
        with override_settings(ALIYUN_API_KEY=""):
            with patch("myapp.utils.llm_client.requests.post") as mock_post:
                result = call_aliyun_llm("你好")
        self.assertIsNone(result)
        mock_post.assert_not_called()

    def test_success_returns_content_and_builds_payload(self):
        """主流程：正常响应时返回模型内容，并正确构造请求参数"""
        fake_resp = MagicMock()
        fake_resp.json.return_value = {"choices": [{"message": {"content": "推荐盖饭"}}]}

        with override_settings(
            ALIYUN_API_KEY="test-key",
            ALIYUN_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1",
            ALIYUN_MODEL="qwen-plus",
        ):
            with patch("myapp.utils.llm_client.requests.post", return_value=fake_resp) as mock_post:
                result = call_aliyun_llm("推荐美食", system_prompt="你是平台助手", temperature=0.5, max_tokens=256)

        self.assertEqual(result, "推荐盖饭")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-key")
        payload = kwargs["json"]
        self.assertEqual(payload["model"], "qwen-plus")
        self.assertEqual(payload["temperature"], 0.5)
        self.assertEqual(payload["max_tokens"], 256)
        self.assertEqual(payload["messages"][0], {"role": "system", "content": "你是平台助手"})
        self.assertEqual(payload["messages"][1], {"role": "user", "content": "推荐美食"})

    def test_network_exception_returns_none(self):
        """异常分支：网络异常（如连接失败）返回 None"""
        with override_settings(ALIYUN_API_KEY="test-key"):
            with patch(
                "myapp.utils.llm_client.requests.post",
                side_effect=requests.exceptions.ConnectionError("boom"),
            ) as mock_post:
                result = call_aliyun_llm("你好")
        self.assertIsNone(result)
        mock_post.assert_called_once()

    def test_http_error_returns_none(self):
        """异常分支：HTTP 非 2xx 状态码返回 None"""
        fake_resp = MagicMock()
        fake_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        with override_settings(ALIYUN_API_KEY="test-key"):
            with patch("myapp.utils.llm_client.requests.post", return_value=fake_resp):
                result = call_aliyun_llm("你好")
        self.assertIsNone(result)


class AdminRequiredDecoratorTest(TestCase):
    """管理员权限装饰器 admin_required 单元测试"""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create(username="admin1", password="abc12345", phone="13800000008", usertype=3)
        cls.normal = User.objects.create(username="user1", password="abc12345", phone="13800000009", usertype=0)

    def test_not_logged_in_redirects_to_login(self):
        """异常分支：未登录访问被重定向到登录页"""
        request = RequestFactory().get("/manage/")
        request.session = {}
        response = admin_views.admin_required(lambda r: None)(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

    def test_non_admin_redirects_to_login(self):
        """异常分支：非管理员（普通用户）访问被重定向"""
        request = RequestFactory().get("/manage/")
        request.session = {"user_id": self.normal.id}
        response = admin_views.admin_required(lambda r: None)(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/account/login/")

    def test_admin_passes_and_gets_app_admin(self):
        """主流程：管理员访问可进入，request.app_admin 指向当前管理员"""
        captured = {}

        def view(request):
            captured["admin"] = request.app_admin
            return "OK"

        request = RequestFactory().get("/manage/")
        request.session = {"user_id": self.admin.id}
        response = admin_views.admin_required(view)(request)
        self.assertEqual(response, "OK")
        self.assertEqual(captured["admin"], self.admin)

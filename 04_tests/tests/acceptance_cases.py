"""Traceable end-to-end acceptance cases from the project use-case list."""

USE_CASES = (
    {
        "id": "UC01",
        "title": "建立账号并进入角色工作台",
        "representative": False,
        "tests": (
            "tests.test_e2e.AccountRegistrationE2ETest.test_uc01_main_flow",
            "tests.test_e2e.AccountRegistrationE2ETest.test_uc01_abnormal_branches",
        ),
    },
    {
        "id": "UC02",
        "title": "完成外卖下单、配送履约与评价",
        "representative": True,
        "tests": (
            "tests.test_e2e.FoodDeliveryE2ETest.test_full_food_delivery_scenario",
            "tests.test_e2e.CartToOrderE2ETest.test_full_cart_scenario",
            "tests.test_e2e.FoodDeliveryE2ETest.test_uc02_abnormal_branches",
        ),
    },
    {
        "id": "UC03",
        "title": "购买并核销到店团购券",
        "representative": False,
        "tests": (
            "tests.test_e2e.GroupBuyE2ETest.test_full_group_buy_scenario",
            "tests.test_e2e.GroupBuyE2ETest.test_uc03_abnormal_branches",
        ),
    },
    {
        "id": "UC04",
        "title": "预订酒店并评价入住体验",
        "representative": True,
        "tests": (
            "tests.test_e2e.HotelE2ETest.test_full_hotel_scenario",
            "tests.test_e2e.HotelE2ETest.test_uc04_abnormal_branches",
        ),
    },
    {
        "id": "UC05",
        "title": "购买娱乐门票并评价体验",
        "representative": False,
        "tests": (
            "tests.test_e2e.PlayE2ETest.test_full_play_scenario",
            "tests.test_e2e.PlayE2ETest.test_uc05_abnormal_branches",
        ),
    },
    {
        "id": "UC06",
        "title": "发布并维护商家服务供给",
        "representative": False,
        "tests": (
            "tests.test_e2e.MerchantSupplyE2ETest.test_uc06_main_flow",
            "tests.test_e2e.MerchantSupplyE2ETest.test_uc06_abnormal_branches",
        ),
    },
    {
        "id": "UC07",
        "title": "发布内容并参与社区互动",
        "representative": True,
        "tests": (
            "tests.test_e2e.BlogE2ETest.test_full_blog_scenario",
            "tests.test_e2e.BlogE2ETest.test_uc07_abnormal_branches",
        ),
    },
    {
        "id": "UC08",
        "title": "获取个性化 AI 咨询",
        "representative": False,
        "tests": (
            "tests.test_e2e.AiAssistantE2ETest.test_full_ai_assistant_scenario",
            "tests.test_e2e.AiAssistantE2ETest.test_uc08_abnormal_branches",
        ),
    },
    {
        "id": "UC09",
        "title": "开展平台运营治理",
        "representative": False,
        "tests": (
            "tests.test_e2e.AdminE2ETest.test_full_admin_scenario",
            "tests.test_e2e.AdminE2ETest.test_uc09_abnormal_branches",
        ),
    },
)

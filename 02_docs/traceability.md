# 最新需求追溯表（可编辑基线）

更新日期：2026-08-31

旧版 `追溯表.pdf` 是 2026-08-25 的组内基线（104 项测试、Python 3.10.10 / Django 5.2.14），不能替代本表。当前可复现实测结果见 `04_tests/tests/test_report.*` 和 `04_tests/tests/microservice_test_report.*`。

| 需求 | 用例 | 三层模型 | 代码模块 | 单元测试 | 集成/API 测试 | 单体 E2E | 微服务 E2E | 当前结果 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REQ01 | UC01 账号与角色工作台 | SYS/COMP/OBJ-SEQ01 | `myapp.views.register/login/logout_view`、`admin_views.admin_required` | `PasswordBusinessRuleTest`、`UserHelperRuleTest` | `AuthApiTest` | `AccountRegistrationE2ETest` | 待补 | 单体通过 |
| REQ02 | UC02 外卖下单、履约与评价 | SYS/COMP/OBJ-SEQ02 | `views.food/foodorder/ordercomment`、`service_views.rider_*` | 订单/评分规则测试 | `FoodApiTest`、`CrossModuleIntegrationTest` | `FoodDeliveryE2ETest`、`CartToOrderE2ETest` | 待补 | 单体通过 |
| REQ03 | UC03 团购券购买与核销 | SYS/COMP/OBJ-SEQ03 | `views.groupbuyorder/make_group_buy_code`、`service_views.groupbuy_redeem` | `GroupBuyCodeRuleTest` | `GroupBuyApiTest` | `GroupBuyE2ETest` | 待补 | 单体通过 |
| REQ04 | UC04 酒店预订与评价 | SYS/COMP/OBJ-SEQ04 | `service_views.hotel/hotelorder/hotelcomment` | `HotelPriceRuleTest`、`HotelReviewRuleTest` | `HotelApiTest` | `HotelE2ETest` | 待补 | 单体通过 |
| REQ05 | UC05 娱乐购票与评价 | SYS/COMP/OBJ-SEQ05 | `service_views.play/playorder/playcomment` | `PlayReviewRuleTest` | `PlayApiTest` | `PlayE2ETest` | 待补 | 单体通过 |
| REQ06 | UC06 商家发布与维护供给 | SYS/COMP/OBJ-SEQ06 | `views.foodsend`、`service_views.hotelsend/playsend`、`merchant_food_action` | 角色/模型校验 | `FoodApiTest`、`CrossModuleIntegrationTest` | `MerchantSupplyE2ETest` | 待补 | 单体通过 |
| REQ07 | UC07 博客与社区互动 | SYS/COMP/OBJ-SEQ07 | `views.blog/blogsend/blogcomment/delete_*` | 内容边界规则 | `BlogApiTest` | `BlogE2ETest` | 待补 | 单体通过 |
| REQ08 | UC08 AI 个性化咨询 | SYS/COMP/OBJ-SEQ08 | `views.ai_chat_view/get_global_info`、`utils.llm_client` | `LlmClientTest` | `AiApiTest` | `AiAssistantE2ETest`（外部调用 mock） | 待补 | 单体通过 |
| REQ09 | UC09 平台运营治理 | SYS/COMP/OBJ-SEQ09 | `admin_views.admin_dashboard/admin_*_action` | `AdminRequiredDecoratorTest` | `AdminApiTest` | `AdminE2ETest` | 待补 | 单体通过 |

## 微服务模型与接口证据

- 系统级、组件级、对象级顺序图：`02_docs/requirements/`、`02_docs/design/overview/`、`02_docs/design/detailed/` 中的 9 用例 PDF。
- 服务划分、服务接口清单、数据表归属和跨服务失败处理：`02_docs/微服务拆分方案.md`。
- 微服务隔离 API/契约结果：`04_tests/tests/microservice_test_report.md`，当前 24 项测试覆盖 54 个公开 API 方法。
- 微服务经网关的 UC01-UC09 端到端回归仍是 P1 任务，完成后必须把本表“微服务 E2E”列替换为实际测试编号和结果。

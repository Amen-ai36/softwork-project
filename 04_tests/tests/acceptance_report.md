# 业务用例端到端验收报告

- 生成时间：2026-08-29 15:57:38
- 用例清单：UC01-UC09
- 通过用例：9/9
- 总体结果：OK

## 代表性用例

| 用例 | 业务场景 | 自动化证据数 | 结果 |
| --- | --- | ---: | --- |
| UC02 | 完成外卖下单、配送履约与评价 | 3 | PASSED |
| UC04 | 预订酒店并评价入住体验 | 2 | PASSED |
| UC07 | 发布内容并参与社区互动 | 2 | PASSED |

## 全部业务用例

| 用例 | 业务场景 | 主流程/异常流程证据 | 结果 |
| --- | --- | ---: | --- |
| UC01 | 建立账号并进入角色工作台 | 2 | PASSED |
| UC02 | 完成外卖下单、配送履约与评价 | 3 | PASSED |
| UC03 | 购买并核销到店团购券 | 2 | PASSED |
| UC04 | 预订酒店并评价入住体验 | 2 | PASSED |
| UC05 | 购买娱乐门票并评价体验 | 2 | PASSED |
| UC06 | 发布并维护商家服务供给 | 2 | PASSED |
| UC07 | 发布内容并参与社区互动 | 2 | PASSED |
| UC08 | 获取个性化 AI 咨询 | 2 | PASSED |
| UC09 | 开展平台运营治理 | 2 | PASSED |

## 测试证据

### UC01 建立账号并进入角色工作台

- `tests.test_e2e.AccountRegistrationE2ETest.test_uc01_main_flow`：PASSED
- `tests.test_e2e.AccountRegistrationE2ETest.test_uc01_abnormal_branches`：PASSED

### UC02 完成外卖下单、配送履约与评价

- `tests.test_e2e.FoodDeliveryE2ETest.test_full_food_delivery_scenario`：PASSED
- `tests.test_e2e.CartToOrderE2ETest.test_full_cart_scenario`：PASSED
- `tests.test_e2e.FoodDeliveryE2ETest.test_uc02_abnormal_branches`：PASSED

### UC03 购买并核销到店团购券

- `tests.test_e2e.GroupBuyE2ETest.test_full_group_buy_scenario`：PASSED
- `tests.test_e2e.GroupBuyE2ETest.test_uc03_abnormal_branches`：PASSED

### UC04 预订酒店并评价入住体验

- `tests.test_e2e.HotelE2ETest.test_full_hotel_scenario`：PASSED
- `tests.test_e2e.HotelE2ETest.test_uc04_abnormal_branches`：PASSED

### UC05 购买娱乐门票并评价体验

- `tests.test_e2e.PlayE2ETest.test_full_play_scenario`：PASSED
- `tests.test_e2e.PlayE2ETest.test_uc05_abnormal_branches`：PASSED

### UC06 发布并维护商家服务供给

- `tests.test_e2e.MerchantSupplyE2ETest.test_uc06_main_flow`：PASSED
- `tests.test_e2e.MerchantSupplyE2ETest.test_uc06_abnormal_branches`：PASSED

### UC07 发布内容并参与社区互动

- `tests.test_e2e.BlogE2ETest.test_full_blog_scenario`：PASSED
- `tests.test_e2e.BlogE2ETest.test_uc07_abnormal_branches`：PASSED

### UC08 获取个性化 AI 咨询

- `tests.test_e2e.AiAssistantE2ETest.test_full_ai_assistant_scenario`：PASSED
- `tests.test_e2e.AiAssistantE2ETest.test_uc08_abnormal_branches`：PASSED

### UC09 开展平台运营治理

- `tests.test_e2e.AdminE2ETest.test_full_admin_scenario`：PASSED
- `tests.test_e2e.AdminE2ETest.test_uc09_abnormal_branches`：PASSED

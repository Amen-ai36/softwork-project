# The Food Master — 用例说明与需求追溯

编号约定（贯穿需求、设计、代码、测试）：

| 前缀 | 含义 | 示例 |
|------|------|------|
| REQ | 业务需求 | REQ01 |
| UC | 用例 | UC01 |
| SYS-SEQ | 系统级时序图 | SYS-SEQ01 |
| COMP-SEQ | 组件/模块级时序图 | COMP-SEQ01 |
| OBJ-SEQ | 对象/类级时序图 | OBJ-SEQ01 |
| UNIT-TC | 单元测试用例 | UNIT-TC01 |
| INT-TC | 集成测试用例 | INT-TC01 |
| E2E-TC | 端到端/流程测试用例 | E2E-TC01 |

对应关系串示例：

`REQ02 / UC02 / SYS-SEQ02 / COMP-SEQ02 / OBJ-SEQ02 / UNIT-TC02 / INT-TC02 / E2E-TC02`

> 说明：仓库内暂无独立绘图文件；`SYS-SEQ*` / `COMP-SEQ*` / `OBJ-SEQ*` 为汇报用设计图编号，应与下文「主成功流程」步骤一一对应绘制。测试编号已映射到 `test/test_project_workflows.py` 中的实际方法。应用源码位于 `src/`（如 `src/myapp/views.py`、`src/templates/`）。

---

## 一、用例总览与追溯索引

| 编号 | 用例名称 | 主要参与者 | 核心代码 | 主要测试 |
|------|----------|------------|----------|----------|
| UC01 | 注册与按身份登录 | 访客、系统 | `views.register` / `views.login` | `test_register_login_and_role_redirects` |
| UC02 | 美食外卖全链路下单配送评价 | 用户、骑手、商家 | `foodorder`→`rider_*`→`merchant_prepare`→`ordercomment` | `test_food_order_full_delivery_and_review_flow` |
| UC03 | 到店团购购买与核销 | 用户、商家 | `groupbuyorder` / `groupbuy_redeem` | `test_group_buy_coupon_create_display_and_redeem_flow` |
| UC04 | 酒店预订与评价 | 用户 | `views1.hotelorder` / `hotelcomment` | `test_hotel_booking_and_review_flow` |
| UC05 | 娱乐购票与评价 | 用户 | `views1.playorder` / `playcomment` | `test_play_ticket_order_and_review_flow` |
| UC06 | 商家上架美食/酒店/娱乐 | 商家 | `foodsend` / `hotelsend` / `playsend` | `test_merchant_can_create_food_hotel_and_play_with_uploads` |
| UC07 | 骑手接单中心操作 | 骑手 | `rider_orders` / `rider_accept` 等 | `test_cross_role_food_order_visibility_and_response_flow` |
| UC08 | 博客发布评论删除 | 用户 | `blog*` / `delete_*` | `test_blog_comment_and_delete_flow` |
| UC09 | AI 助手对话 | 用户 | `ai_chat_view` / `llm_client` | `test_ai_chat_endpoint_uses_catalog_context_without_live_network` |
| UC10 | 管理员治理 | 管理员 | `admin_views.*` | `test_admin_dashboard_and_actions` |
| UC11 | 购物车加购与结算 | 用户 | `Temp` + cart 相关视图 | （测试 README 标明部分未单独覆盖） |
| UC12 | 列表搜索与排序 | 用户 | `food` / `hotel` / `play` | `test_food_listing_*` 等 |

---

## 二、各用例说明（统一模板）

### UC01 注册与按身份登录

| 项 | 内容 |
|----|------|
| **需求** | REQ01 系统应支持访客注册（普通用户/骑手/商家）并按身份登录跳转 |
| **参与者** | 访客；系统 |
| **触发条件** | 用户打开 `/account/register/` 或 `/account/login/` 并提交表单 |
| **前置条件** | 数据库可写；注册时用户名未被占用；登录时账号已存在且未停用 |
| **主成功流程** | ① 填写用户名、密码、手机号、身份 → ② 校验通过创建 `User` → ③ 跳转登录页 → ④ 输入凭证与身份 → ⑤ Session 写入 `user_id` → ⑥ 按身份跳转（用户→`/food/`，骑手→`/rider/`，管理员→`/manage/`） |
| **备选/异常** | 密码不符合 8–16 位字母数字组合；用户名已存在；密码错误；身份选择与账号不符；账号 `isDelete=True`；试图注册管理员 |
| **可验证结果** | `User` 记录存在；登录后 Session 有 `user_id`；HTTP 302 到对应首页 |
| **设计图** | SYS-SEQ01 / COMP-SEQ01 / OBJ-SEQ01 |
| **代码** | `src/myapp/views.py`：`register`、`login`；模板 `src/templates/register.html`、`login.html`；路由 `src/food_master/urls.py` |
| **测试** | INT-TC01 / E2E-TC01 → `test_register_login_and_role_redirects`；UNIT-TC01 → 密码正则与 `usertype` 分支（可从同文件抽出或补充） |

---

### UC02 美食外卖全链路（下单→接单→备餐→取餐→送达→评价）

| 项 | 内容 |
|----|------|
| **需求** | REQ02 用户可点外卖；订单状态按 0→1→2→3→4→5 由多角色协作推进 |
| **参与者** | 普通用户、骑手、商家；系统 |
| **触发条件** | 已登录用户在菜品详情发起下单（`cutlery=1` 直接下单） |
| **前置条件** | 用户 Session 有效；菜品存在且未下架/未售罄；各角色身份正确 |
| **主成功流程** | 见第三节详细展开 |
| **备选/异常** | 未登录；菜品不存在/下架/售罄；信息不完整；非骑手接单；订单已被他人接走；非商家备餐；非本单骑手取餐/送达；评分非法 |
| **可验证结果** | `Order.pos` 依次为 0,1,2,3,4,5；费用=`price*num`；骑手绑定；评价字段写入 |
| **设计图** | SYS-SEQ02 / COMP-SEQ02 / OBJ-SEQ02 |
| **代码** | `views.foodorder`、`views1.rider_accept/get/deliver`、`views1.merchant_prepare`、`views.ordercomment`；模型 `Order`/`Food` |
| **测试** | E2E-TC02 → `test_food_order_full_delivery_and_review_flow`；INT-TC02 → `test_cross_role_food_order_visibility_and_response_flow` |

---

### UC03 到店团购购买与核销

| 项 | 内容 |
|----|------|
| **需求** | REQ03 用户可购买到店团购券；所属商家凭核销码核销 |
| **参与者** | 普通用户、商家；系统 |
| **触发条件** | 用户 POST `/groupbuyorder/`；商家 POST `/groupbuy/redeem/` |
| **前置条件** | 用户已登录；菜品可售；核销时操作者为该菜品商家 |
| **主成功流程** | ① 选菜品团购 → ② 填数量生成 `GroupBuyCoupon`(status=0, 唯一 code) → ③ 用户个人中心可见 → ④ 商家输入核销码 → ⑤ status=1，写入 `used_at` |
| **备选/异常** | 数量非法；菜品下架/售罄；非商家核销；码不存在/不属于本店；已核销/已取消 |
| **可验证结果** | 券记录正确；核销后状态与时间更新；他店商家无法核销 |
| **设计图** | SYS-SEQ03 / COMP-SEQ03 / OBJ-SEQ03 |
| **代码** | `views.groupbuyorder`、`groupbuy_redeem`、`make_group_buy_code`；模型 `GroupBuyCoupon` |
| **测试** | E2E-TC03 → `test_group_buy_coupon_create_display_and_redeem_flow` |

---

### UC04 酒店预订与评价

| 项 | 内容 |
|----|------|
| **需求** | REQ04 用户可预订酒店房型并在入住后评价，评分回写酒店 |
| **参与者** | 普通用户；系统 |
| **触发条件** | POST `/hotelorder/`；POST `/hotelcomment/` |
| **前置条件** | 已登录；酒店存在；评价时订单属本人且 `pos=4` |
| **主成功流程** | 选房型与时长 → 创建 `HotelOrder`(pos=4, cost 按价计算) → 评价 → pos=5，更新 `Hotel.rating/ratenum` |
| **备选/异常** | 未登录；参数错误；查看他人订单被拒绝；评分非法 |
| **可验证结果** | 订单费用正确；评价后酒店均分与人数更新 |
| **设计图** | SYS-SEQ04 / COMP-SEQ04 / OBJ-SEQ04 |
| **代码** | `views1.hotelorder`、`hotelcomment`、`save_hotel_review` |
| **测试** | E2E-TC04 → `test_hotel_booking_and_review_flow`；INT-TC04 → `test_hotel_listing_search_detail_order_status_and_permissions` |

---

### UC05 娱乐购票与评价

| 项 | 内容 |
|----|------|
| **需求** | REQ05 用户可购买娱乐门票并评价 |
| **参与者** | 普通用户；系统 |
| **触发条件** | POST `/playorder/`；POST `/playcomment/` |
| **前置条件** | 已登录；场所存在 |
| **主成功流程** | 选票数与时间 → `PlayOrder` → 评价 → 更新 `Play` 评分 |
| **备选/异常** | 权限与参数错误；非本人订单 |
| **可验证结果** | 订单与评分字段符合预期 |
| **设计图** | SYS-SEQ05 / COMP-SEQ05 / OBJ-SEQ05 |
| **代码** | `views1.playorder`、`playcomment` |
| **测试** | E2E-TC05 → `test_play_ticket_order_and_review_flow` |

---

### UC06 商家上架资源（含图片）

| 项 | 内容 |
|----|------|
| **需求** | REQ06 商家可创建美食/酒店/娱乐并上传 &lt;2MB 图片 |
| **参与者** | 商家；系统 |
| **触发条件** | 商家访问 `/foodsend/`、`/hotelsend/`、`/playsend/` 并提交 |
| **前置条件** | Session 用户 `usertype=2` |
| **主成功流程** | 校验身份 → 接收表单与图片 → 落盘 static → 创建模型并关联 `merchant` |
| **备选/异常** | 非商家拒绝；图片过大/格式非法；必填缺失 |
| **可验证结果** | 新记录 `merchant_id` 正确；列表页可见 |
| **设计图** | SYS-SEQ06 / COMP-SEQ06 / OBJ-SEQ06 |
| **代码** | `views.foodsend`、`views1.hotelsend`、`views1.playsend` |
| **测试** | E2E-TC06 → `test_merchant_can_create_food_hotel_and_play_with_uploads`；INT-TC06 → `test_role_permissions_are_enforced` |

---

### UC07 骑手接单中心

| 项 | 内容 |
|----|------|
| **需求** | REQ07 骑手可查看待接单并推进配送状态 |
| **参与者** | 骑手；系统 |
| **触发条件** | 访问 `/rider/` 或接单/取餐/送达 URL |
| **前置条件** | `usertype=1`；目标订单状态匹配 |
| **主成功流程** | 列表 pos=0 → 接单绑定 rider → 商家备餐后取餐 → 送达 |
| **备选/异常** | 非骑手；订单已被接；订单不属于该骑手 |
| **可验证结果** | 页面展示待接单；状态与 `rider_id` 正确 |
| **设计图** | SYS-SEQ07（可与 UC02 共用子系统图） |
| **代码** | `views1.rider_orders` 等 |
| **测试** | INT-TC07 → `test_cross_role_food_order_visibility_and_response_flow` |

---

### UC08 博客发布与评论

| 项 | 内容 |
|----|------|
| **需求** | REQ08 用户可发帖、评论、删除本人内容 |
| **参与者** | 用户；系统 |
| **触发条件** | `/blogsend/`、`/blogcomment/`、删除接口 |
| **前置条件** | 已登录 |
| **主成功流程** | 发帖 → 列表/详情 → 评论 → 逻辑删除 |
| **备选/异常** | 未登录；删他人内容失败 |
| **可验证结果** | `Blog`/`Comment` 记录与 `isdeleted` 标志 |
| **设计图** | SYS-SEQ08 / COMP-SEQ08 / OBJ-SEQ08 |
| **代码** | `views.blog*`、`delete_blog`、`delete_comment` |
| **测试** | E2E-TC08 → `test_blog_comment_and_delete_flow` |

---

### UC09 AI 助手对话

| 项 | 内容 |
|----|------|
| **需求** | REQ09 登录用户可与 AI 对话，上下文含平台目录数据 |
| **参与者** | 用户；系统；外部 LLM（可 mock） |
| **触发条件** | 请求 `/ai-chat/` |
| **前置条件** | 已登录；配置 API Key（测试中 mock） |
| **主成功流程** | 收用户输入 → 组装含美食/酒店/娱乐的 system prompt → 调 LLM → 返回 JSON |
| **备选/异常** | 外部服务失败；未登录 |
| **可验证结果** | 响应 JSON；prompt 含目录数据；无真实外网依赖（测试） |
| **设计图** | SYS-SEQ09 / COMP-SEQ09 / OBJ-SEQ09 |
| **代码** | `views.ai_chat_view`、`src/myapp/utils/llm_client.py` |
| **测试** | INT-TC09 → `test_ai_chat_endpoint_uses_catalog_context_without_live_network` |

---

### UC10 管理员治理

| 项 | 内容 |
|----|------|
| **需求** | REQ10 管理员可停用用户、处理订单、审核博客 |
| **参与者** | 管理员；系统 |
| **触发条件** | 访问 `/manage/` 及相关 action |
| **前置条件** | `usertype=3` |
| **主成功流程** | 进入后台 → 停用用户 / 完成订单 / 删除博客 → 退出 |
| **备选/异常** | 普通用户访问被重定向登录 |
| **可验证结果** | `isDelete`、订单 `pos`、博客 `isdeleted` 变化 |
| **设计图** | SYS-SEQ10 / COMP-SEQ10 / OBJ-SEQ10 |
| **代码** | `src/myapp/admin_views.py` |
| **测试** | E2E-TC10 → `test_admin_dashboard_and_actions` |

---

### UC11 购物车

| 项 | 内容 |
|----|------|
| **需求** | REQ11 用户可将外卖加入购物车后统一结算 |
| **参与者** | 用户；系统 |
| **触发条件** | 下单时非直接下单路径写入 `Temp`；cart 更新/删除/清空 |
| **前置条件** | 已登录 |
| **主成功流程** | 加购 → 改数量/删项 → 结算生成订单 |
| **备选/异常** | 空车结算；未登录 |
| **可验证结果** | `Temp`/`Order` 数据一致 |
| **设计图** | SYS-SEQ11 |
| **代码** | `update_cart_item`、`delete_cart_item`、`clear_cart`、`foodorder` 中 Temp 分支 |
| **测试** | 自动化覆盖较弱，建议补 INT-TC11 / 人工 E2E |

---

### UC12 浏览搜索排序

| 项 | 内容 |
|----|------|
| **需求** | REQ12 用户可按关键字搜索、按价格/销量/评分排序 |
| **参与者** | 用户；系统 |
| **触发条件** | GET 列表页带 `q` / 排序参数 |
| **前置条件** | 通常需登录（与现有视图一致） |
| **主成功流程** | 打开列表 → 输入关键字/选排序 → 渲染过滤结果 |
| **备选/异常** | 无匹配结果 |
| **可验证结果** | 响应含目标条目、不含无关条目 |
| **设计图** | SYS-SEQ12 |
| **代码** | `views.food`、`views1.hotel`、`views1.play` |
| **测试** | INT-TC12 → `test_food_listing_search_detail_order_status_and_space_queries` 等 |

---

## 三、汇报重点：3 个代表性用例的完整对应链

以下 3 个用例覆盖「账号入口 / 多角色核心业务 / 增值业务」，适合最终答辩详细展示。

---

### 代表性用例 A：REQ01 / UC01 / SYS-SEQ01 / COMP-SEQ01 / OBJ-SEQ01 / UNIT-TC01 / INT-TC01 / E2E-TC01

**主题：注册与按身份登录**

#### 用例说明摘要
- **参与者**：访客、系统  
- **触发**：提交注册或登录表单  
- **前置**：库可用；登录账号存在且未停用  
- **主成功流**：注册校验 → 写 `User` → 登录校验身份 → Session → 角色首页  
- **异常流**：弱密码、重名、错密、错身份、停用账号  
- **可验证结果**：用户落库；302 到 `/food/`、`/rider/` 或 `/manage/`

#### 设计图应表达的内容
| 图号 | 层级 | 建议泳道/对象 |
|------|------|----------------|
| SYS-SEQ01 | 系统 | 浏览器 ↔ Web 应用 ↔ MySQL |
| COMP-SEQ01 | 组件 | Template → `urls` → `views.login/register` → ORM |
| OBJ-SEQ01 | 对象 | `Client/Request` → `login()` → `User.objects` → `session` → `redirect` |

#### 代码锚点
```
REQ01 → UC01
  → src/food_master/urls.py          path("account/login/"), path("account/register/")
  → src/myapp/views.py               login(), register()
  → src/myapp/models.py              User (usertype, isDelete, password)
  → src/templates/login.html, register.html
```

#### 测试锚点
| 测试编号 | 类型 | 实际方法 | 断言要点 |
|----------|------|----------|----------|
| UNIT-TC01 | 单元 | （建议补充）密码正则、`usertype` 边界 | 非法密码/管理员注册被拒 |
| INT-TC01 | 集成 | `test_core_routes_resolve_to_expected_views` 中 login/register 路由 | resolve 到正确视图名 |
| E2E-TC01 | 端到端 | `test_register_login_and_role_redirects` | 注册 302→登录页；用户→`/food/`；骑手→`/rider/`；管理员→`/manage/` |

---

### 代表性用例 B：REQ02 / UC02 / SYS-SEQ02 / COMP-SEQ02 / OBJ-SEQ02 / UNIT-TC02 / INT-TC02 / E2E-TC02

**主题：美食外卖全链路（最能体现多角色协作）**

#### 用例说明

| 项 | 内容 |
|----|------|
| **参与者** | 普通用户、骑手、商家、系统 |
| **触发条件** | 用户提交外卖订单（直接下单） |
| **前置条件** | 三角色均已登录；菜品可售 |
| **主成功流程** | 见下表 |
| **备选/异常** | 未登录重定向；下架/售罄；抢单失败；越权操作；评分越界 |
| **可验证结果** | `pos`: 0→1→2→3→4→5；`cost`；`rider`；评分字段 |

#### 主成功流程（逐步 ↔ 设计图步骤 ↔ 代码 ↔ 测试）

| 步 | 行为 | 状态 | URL / 函数 | 设计图步骤 |
|----|------|------|------------|------------|
| 1 | 用户下单 | pos=0 | `POST /foodorder/?foodid=` → `views.foodorder` | SYS-SEQ02:1 |
| 2 | 骑手接单 | 0→1，绑定 rider | `GET /rider_accept/` → `rider_accept` | SYS-SEQ02:2 |
| 3 | 商家备餐 | 1→2 | `GET /merchant_prepare/` → `merchant_prepare` | SYS-SEQ02:3 |
| 4 | 骑手取餐 | 2→3 | `GET /rider_get/` → `rider_get` | SYS-SEQ02:4 |
| 5 | 骑手送达 | 3→4 | `GET /rider_deliver/` → `rider_deliver` | SYS-SEQ02:5 |
| 6 | 用户评价 | 4→5 | `POST /ordercomment/` → `ordercomment` | SYS-SEQ02:6 |

#### COMP-SEQ02 / OBJ-SEQ02 建议
- **COMP-SEQ02**：User UI / Rider UI / Merchant UI → Django Views → `Order` 表  
- **OBJ-SEQ02**：`Order` 对象上 `pos`/`rider`/`score*` 字段变更序列；可画状态机旁注

#### 代码锚点
```
src/myapp/views.py        foodorder(), ordercomment(), sync_food_sales()
src/myapp/views1.py       rider_accept(), merchant_prepare(), rider_get(), rider_deliver()
src/myapp/models.py       Order, Food
src/templates/food/foodorder.html
src/templates/foodorder/ordercomment.html
src/templates/rider_orders.html
src/templates/space.html  （跨角色可见性）
```

#### 测试锚点
| 测试编号 | 实际方法 | 覆盖点 |
|----------|----------|--------|
| UNIT-TC02 | （可选补充）对 `pos` 迁移辅助函数或 `sync_food_sales` | 销量同步 |
| INT-TC02 | `test_cross_role_food_order_visibility_and_response_flow` | 各角色页面能否看到订单与按钮 |
| E2E-TC02 | `test_food_order_full_delivery_and_review_flow` | 全状态链 + 评分断言 |

运行：

```powershell
cd src
python manage.py test test.FAKESECRET_c1d2e3f4g5h6i7j8k9l0 -v 2
```

---

### 代表性用例 C：REQ03 / UC03 / SYS-SEQ03 / COMP-SEQ03 / OBJ-SEQ03 / UNIT-TC03 / INT-TC03 / E2E-TC03

**主题：到店团购购买与商家核销**

#### 用例说明

| 项 | 内容 |
|----|------|
| **参与者** | 普通用户、商家、系统 |
| **触发条件** | 用户提交团购；商家提交核销码 |
| **前置条件** | 用户已登录；菜品可售；核销人为该菜 `merchant` |
| **主成功流程** | 创建券(status=0) → 用户/商家个人中心可见 → 核销(status=1, used_at) |
| **备选/异常** | 非法数量；非商家；码错误/他店；重复核销 |
| **可验证结果** | `GroupBuyCoupon` 字段；页面文案「待使用」「已使用」 |

#### 设计图
| 图号 | 内容 |
|------|------|
| SYS-SEQ03 | 用户浏览器 ↔ 系统 ↔ 商家浏览器；共享 `GroupBuyCoupon` |
| COMP-SEQ03 | `groupbuyorder` 视图 ↔ ORM ↔ `groupbuy_redeem` 视图 |
| OBJ-SEQ03 | `GroupBuyCoupon`：create → status 0→1；`make_group_buy_code()` |

#### 代码锚点
```
src/myapp/views.py     groupbuyorder(), groupbuy_redeem(), make_group_buy_code()
src/myapp/models.py    GroupBuyCoupon
src/templates/food/groupbuy_order.html, groupbuy_success.html
src/templates/space.html
src/food_master/urls.py   groupbuyorder/, groupbuy/redeem/
```

#### 测试锚点
| 测试编号 | 实际方法 | 覆盖点 |
|----------|----------|--------|
| UNIT-TC03 | （可选）`make_group_buy_code` 唯一性 | code 生成 |
| INT-TC03 | 同 E2E 方法内商家/用户 `/space/` 展示断言 | 跨页面可见性 |
| E2E-TC03 | `test_group_buy_coupon_create_display_and_redeem_flow` | 购券→核销→他店拒绝 |

---

## 四、汇报时建议的一页对应关系表（可直接贴幻灯片）

### 用例 B（推荐作为主展示）

```text
REQ02 外卖全链路需求
  └─ UC02 美食外卖全链路用例说明
       ├─ SYS-SEQ02  用户/骑手/商家 ↔ Web ↔ DB
       ├─ COMP-SEQ02  views 层多入口协作
       ├─ OBJ-SEQ02   Order.pos 状态迁移
       ├─ UNIT-TC02   （销量同步/状态校验，可补充）
       ├─ INT-TC02    test_cross_role_food_order_visibility_and_response_flow
       └─ E2E-TC02    test_food_order_full_delivery_and_review_flow
            代码：foodorder → rider_accept → merchant_prepare
                  → rider_get → rider_deliver → ordercomment
```

### 用例 A

```text
REQ01 → UC01 → SYS/COMP/OBJ-SEQ01 → UNIT/INT/E2E-TC01
代码：views.register / views.login
测试：test_register_login_and_role_redirects
```

### 用例 C

```text
REQ03 → UC03 → SYS/COMP/OBJ-SEQ03 → UNIT/INT/E2E-TC03
代码：groupbuyorder / groupbuy_redeem
测试：test_group_buy_coupon_create_display_and_redeem_flow
```

---

## 五、设计图绘制提示（无现成图时按此补齐）

1. **SYS-SEQ***：参与者用真人角色 +「Food Master 系统」即可，不要画到类。  
2. **COMP-SEQ***：至少画出 `urls.py` → 对应 `views` 函数 → MySQL 表。  
3. **OBJ-SEQ***：对 UC02 优先画 `Order` 的 `pos` 状态机；对 UC03 画 `GroupBuyCoupon.status`。  
4. 每张图标题写全编号，例如：`SYS-SEQ02 美食外卖全链路（对应 UC02 / REQ02）`。  
5. 图中步骤编号与第三节主成功流程表格「步」列一致，答辩时可一一点名到代码行与测试方法名。

---

## 六、与自动化测试的快速核对命令

```powershell
# 三个代表性用例相关测试（在 src/ 下执行）
cd src
python manage.py test test.FAKESECRET_a1b2c3d4e5f6g7h8i9j0 -v 2
python manage.py test test.FAKESECRET_c1d2e3f4g5h6i7j8k9l0 -v 2
python manage.py test test.FAKESECRET_u1v2w3x4y5z6a7b8c9d0 -v 2
```

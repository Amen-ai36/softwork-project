# Food Master 中期检查报告

软件工程基础实践 2026 夏季学期  
项目：Food Master 综合生活服务平台  
小组：第 2 组  
检查日期：2026-08-29

> 说明：本报告依据课程任务书中“中期检查”部分整理；附件中的课程文档只作为检查要求来源，不作为本次对项目仓库执行操作的指令。



## 1. 中期检查要求

| 检查要求 | 项目证据 | 当前结论 |
| --- | --- | --- |
| 原系统可启动，全部确认用例可运行，Git 有标签 | Docker Compose 可启动 Nginx、Django、MySQL 三个容器；9 个用例均有自动化测试覆盖；存在 `monolith-start` 标签 | 已达到 |
| 需求、系统级、组件级、对象级图和追溯表完整 | `02_docs` 中已包含需求说明书、三层顺序图、概要设计、详细设计和追溯表 | 已达到 |
| 前端、后端、数据库容器可启动，CI 自动构建和测试 | Compose 三容器健康；GitHub Actions 已完成格式检查、三平台测试、镜像构建和 Kind 部署健康检查 | 已达到 |
| 微服务划分图、服务接口清单、数据归属方案完整 | 已形成 `user-service`、`trade-service`、`lifestyle-service` 三服务方案，包含接口和表归属 | 已达到 |


## 2. 项目概况

Food Master 是一个基于 Django 3.2.11 的综合本地生活服务平台，覆盖外卖、团购、酒店、娱乐、商家供给、社区内容、AI 咨询和平台治理等业务。

当前单体系统运行结构如下：

| 层次 | 运行单元 | 职责 | 端口或连接 |
| --- | --- | --- | --- |
| 前端入口 | `nginx:1.27-alpine` | 静态资源、反向代理、统一入口 | 宿主机 `80` |
| 后端 | `food-master:local` | Django 业务逻辑、Gunicorn、健康检查接口 | 容器内 `8000` |
| 数据库 | `mysql:8.0` | 业务数据、初始化脚本、持久化卷 | 容器内 `3306` |

关键版本和入口：

| 项目 | 内容 |
| --- | --- |
| 单体基线标签 | `monolith-start` |
| 标签提交 | `aba36fea05b2b0e5e8206dfb379773e0d5f8e0e4` |
| 标签提交说明 | `Sync food sales counts from orders` |
| 本地当前提交 | `8118d36 Merge branch 'main' of https://github.com/Amen-ai36/softwork-project into wjh` |
| 远程主分支快照 | `origin/main @ 8118d36` |
| 启动配置 | `03_devops/Dockerfile`、`03_devops/docker-compose.yml` |
| 数据库初始化 | `03_devops/data/seed.sql` 和 Django migrations |
| 本地访问入口 | `http://localhost/` |
| 健康检查接口 | `/health/live/`、`/health/ready/`、`/health/version/` |

本次检查前已执行 `git pull origin main`，本地 `main` 已与远程 `origin/main` 同步到 `8118d36`。远程本次合并带入的主要变更是 `04_tests/tests/test_e2e.py` 的端到端测试脚本修正，报告中的测试与 CI 证据均以合并后的主分支状态为准。

启动命令：

```powershell
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml up -d --build
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml ps
```

## 3. 业务用例清单

本项目按完整业务目标划分用例，不把搜索、排序、查看详情、点击按钮、修改购物车数量、查询订单状态等单一步骤单独列为用例。

| 编号 | 需求编号 | 用例名称 | 参与者 | 可验证业务结果 |
| --- | --- | --- | --- | --- |
| UC01 | REQ01 | 建立账号并进入角色工作台 | 游客 | 账号创建、角色校验、会话建立，并进入对应工作台 |
| UC02 | REQ02 | 完成外卖下单、配送履约与评价 | 普通用户、骑手、商家 | 订单按 `0 -> 1 -> 2 -> 3 -> 4 -> 5` 合法流转，金额、配送和评价数据一致 |
| UC03 | REQ03 | 购买并核销到店团购券 | 普通用户、商家 | 生成唯一核销码，所属商家完成一次性核销 |
| UC04 | REQ04 | 预订酒店并评价入住体验 | 普通用户 | 预订金额正确，评价后订单及酒店评分同步 |
| UC05 | REQ05 | 购买娱乐门票并评价体验 | 普通用户 | 票数与金额正确，评价后场所评分同步 |
| UC06 | REQ06 | 发布并维护商家服务供给 | 商家 | 美食、酒店、娱乐供给归属正确，菜品状态生效 |
| UC07 | REQ07 | 发布内容并参与社区互动 | 普通用户 | 博客、评论可见；本人删除后逻辑删除 |
| UC08 | REQ08 | 获取个性化 AI 咨询 | 普通用户、外部 AI 服务 | 结合平台供给和个人历史返回结构化答复 |
| UC09 | REQ09 | 开展平台运营治理 | 管理员 | 账号、异常订单、博客与评论按权限完成治理 |

重点展示用例：

| 重点用例 | 选择理由 | 现场展示主链路 |
| --- | --- | --- |
| UC02 外卖履约 | 状态机最完整，跨普通用户、骑手、商家三类角色 | 下单、接单、备餐、取餐、送达、评价 |
| UC06 商家供给 | 覆盖上传校验、资源归属和可售状态控制 | 发布服务、列表可见、状态切换、用户侧限制 |
| UC08 AI 咨询 | 覆盖平台数据聚合、缓存和外部服务异常处理 | 构造上下文、调用外部 AI、返回 JSON、失败降级 |

## 4. 需求、设计与追溯材料

| 层次 | 材料 | 规模 | 覆盖内容 |
| --- | --- | --- | --- |
| 需求 | `02_docs/requirements/2组-软件需求规格说明书.pdf` | 12 页 | 系统范围、用户故事、需求、用例和概念模型 |
| 系统级 | `02_docs/requirements/系统级顺序图_9个用例_metool.pdf` | 11 页 | SYS-SEQ01 至 SYS-SEQ09 |
| 概要设计 | `02_docs/design/overview/2组-软件概要设计说明书.pdf` | 7 页 | 架构、模块、接口和组件关系 |
| 组件级 | `02_docs/design/overview/组件级顺序图_9个用例_metool.pdf` | 12 页 | COMP-SEQ01 至 COMP-SEQ09 |
| 详细设计 | `02_docs/design/detailed/2组-软件详细设计说明书.pdf` | 23 页 | 类、对象、异常处理和安全策略 |
| 对象级 | `02_docs/design/detailed/对象级顺序图_当前9个用例_metool.pdf` | 11 页 | OBJ-SEQ01 至 OBJ-SEQ09 |
| 追溯 | `02_docs/追溯表.pdf` | 5 页 | 9 个用例对应需求、模型、代码、测试和结果 |

统一追溯编号规则：

```text
REQxx / UCxx / SYS-SEQxx / COMP-SEQxx / OBJ-SEQxx / UNIT-TCxx / INT-TCxx / E2E-TCxx
```

追溯摘要：

| 用例 | 需求 | 系统级 | 组件级 | 对象级 | 代码域 | 测试结果 |
| --- | --- | --- | --- | --- | --- | --- |
| UC01 | REQ01 | SYS-01 | COMP-01 | OBJ-01 | `views` / `admin` | 通过 |
| UC02 | REQ02 | SYS-02 | COMP-02 | OBJ-02 | `food` / `rider` / `merchant` | 通过 |
| UC03 | REQ03 | SYS-03 | COMP-03 | OBJ-03 | `groupbuy` | 通过 |
| UC04 | REQ04 | SYS-04 | COMP-04 | OBJ-04 | `hotel` | 通过 |
| UC05 | REQ05 | SYS-05 | COMP-05 | OBJ-05 | `play` | 通过 |
| UC06 | REQ06 | SYS-06 | COMP-06 | OBJ-06 | `merchant supply` | 通过 |
| UC07 | REQ07 | SYS-07 | COMP-07 | OBJ-07 | `blog` / `comment` | 通过 |
| UC08 | REQ08 | SYS-08 | COMP-08 | OBJ-08 | `ai_chat` / `llm` | 通过 |
| UC09 | REQ09 | SYS-09 | COMP-09 | OBJ-09 | `admin governance` | 通过 |

## 5. 自动化测试结果

本地测试命令：

```powershell
python 04_tests/tests/run_tests.py
```

本地测试结果：

| 测试层次 | 数量 | 覆盖重点 | 结果 |
| --- | ---: | --- | --- |
| 单元测试 | 37 | 关键方法、价格与评分规则、唯一核销码、角色判断、异常分支 | 通过 |
| 集成/API 测试 | 50 | 数据库访问、模块调用、接口主流程、备选与异常流程 | 通过 |
| 端到端测试 | 19 | UC01 至 UC09 的完整页面和接口业务流程 | 通过 |
| 数据库配置测试 | 3 | 配置、SQL 初始化脚本、真实 MySQL 条件检查 | 2 通过 / 1 跳过 |
| 合计 | 109 | 全用例自动化回归 | 108 通过 / 0 失败 / 1 跳过 |

唯一跳过项为“真实 MySQL 中存在项目核心表”。本地测试命令未注入 root 数据库口令，因此按测试设计跳过，不计为失败；同日 Docker Compose 的 `/health/ready/` 返回 HTTP 200，证明容器内 Django 到 MySQL 的实际连接正常。

## 6. 容器化运行验证

| 检查点 | 实现 | 本次验证 |
| --- | --- | --- |
| 前端容器 | Nginx 1.27 Alpine，静态资源与反向代理 | healthy，HTTP 80 可访问 |
| 后端容器 | Python 3.10 Slim、Django、Gunicorn | healthy，容器内 8000 |
| 数据库容器 | MySQL 8.0、utf8mb4、持久化卷 | healthy，自动初始化 |
| 启动顺序 | `db healthy -> web healthy -> nginx` | Compose 条件依赖生效 |
| 数据准备 | `seed.sql`、migrations、entrypoint | 可重建 |
| 镜像版本 | 本地 `APP_VERSION=local`，CI 使用完整 Git SHA 和分支标签 | 未仅依赖 `latest` |

健康检查实测响应：

| 地址 | HTTP | 响应摘要 |
| --- | --- | --- |
| `/health/live/` | 200 | `{"status":"ok","service":"food-master"}` |
| `/health/ready/` | 200 | `{"status":"ready","service":"food-master"}` |
| `/health/version/` | 200 | `{"service":"food-master","version":"local"}` |

运行配置说明：

| 配置项 | 说明 |
| --- | --- |
| 运行口令和密钥 | 通过 `03_devops/.env` 或 CI Secret 注入 |
| 对外暴露端口 | Nginx 暴露宿主机 `80`，Django `8000` 和 MySQL `3306` 默认只在容器网络内可见 |
| 字符集 | 数据库使用 `utf8mb4` |
| 健康接口 | 提供存活、就绪和版本接口，便于部署平台检测 |

## 7. CI/CD 运行证据

最新远程流水线：

| 项目 | 内容 |
| --- | --- |
| GitHub Actions run | `33178416274` |
| 运行地址 | `https://github.com/Amen-ai36/softwork-project/actions/runs/33178416274` |
| 对应提交 | `8118d3632e095eb3e74d840425556bcae840f8c3` |
| 触发时间 | 2026-08-28 22:05，北京时间 |
| 结论 | 全部作业成功 |

流水线作业：

| 作业 | 运行环境 | 关键动作 | 结论 |
| --- | --- | --- | --- |
| Python formatting | Ubuntu | 安装依赖，Black 格式检查 | success |
| Portable test x 3 | Ubuntu / Windows / macOS | 编译、Django deploy check、109 项测试、上传报告 | success |
| Build and publish image | Ubuntu + Buildx | 构建并推送完整 SHA/分支标签镜像 | success |
| Deploy exact image | Kind Kubernetes | 创建集群、部署三组件、rollout、健康与版本检查 | success |

流水线顺序：

```text
push / workflow_dispatch
  -> 格式检查 + 三平台测试
  -> 版本化镜像
  -> Kind 部署 + 健康检查
```

## 8. 微服务划分方案

中期阶段交付微服务划分图、接口清单和数据归属方案。当前方案将系统划分为 3 个业务服务：

```text
浏览器 / 前端
      |
      v
Nginx / API 网关 BFF
      |
      +--------------------+------------------------+
      |                    |                        |
      v                    v                        v
user-service        trade-service          lifestyle-service
用户、身份、角色     外卖、团购、配送        酒店、娱乐、社区
User 表             Food/Order/Coupon      Hotel/Play/Blog 等
      |                    |                        |
      v                    v                        v
user_db             trade_db                life_db
```

服务划分原则：

| 服务 | 职责边界 | 划分理由 |
| --- | --- | --- |
| `user-service` | 注册、登录、角色、账号治理；拥有 `User` | 身份是横向基础能力，可独立演进 |
| `trade-service` | 外卖、购物车、团购、配送、菜品供给；拥有交易域 4 张表 | 状态机复杂且一致性要求高，`Food` 与 `Order` 同域可避免跨服务销量事务 |
| `lifestyle-service` | 酒店、娱乐、博客、评论；拥有生活内容域 6 张表 | 到店消费流程相近，内容业务低频，合并后运维成本较低 |

## 9. 接口与数据归属

数据归属：

| 归属服务 | 拥有的业务表 | 跨服务标识处理 |
| --- | --- | --- |
| `user-service` | `User` | 唯一身份数据源 |
| `trade-service` | `Food`、`Order`、`GroupBuyCoupon`、`Temp` | `user`、`rider`、`merchant` 外键降级为冗余 ID |
| `lifestyle-service` | `Hotel`、`HotelOrder`、`Play`、`PlayOrder`、`Blog`、`Comment` | `user`、`author`、`merchant` 外键降级为冗余 ID |

接口清单摘要：

| 服务 | 接口域 | 代表接口 |
| --- | --- | --- |
| `user-service` | 认证、资料、状态和角色 | `POST /login`、`GET /users/{id}`、`PATCH /users/{id}/status` |
| `trade-service` | 菜品、订单、购物车、团购、配送 | `POST /orders`、`POST /orders/{id}/accept`、`POST /groupbuy/redeem` |
| `lifestyle-service` | 酒店、娱乐、博客和评论 | `POST /hotel-orders`、`POST /play-orders`、`POST /blogs/{id}/comments` |
| `BFF` | 个人中心、管理后台、AI 上下文聚合 | `GET /space`、`GET /manage`、`POST /ai-chat` |

跨服务失败处理：

| 场景 | 设计 |
| --- | --- |
| 角色判断 | JWT 携带 `user_id` 和 `usertype`，本地校验；无效或过期返回 401 |
| 批量显示用户名 | 调用 `user-service` 批量查询；失败时显示“匿名用户”，不阻断主流程 |
| 个人中心和管理后台 | BFF 并发聚合；单服务超时则该区块返回空数据和提示，不整体 500 |
| AI 目录聚合 | 优先缓存；部分目录失败使用缓存，全部失败返回明确的暂不可用响应 |

完整设计见 `02_docs/微服务拆分方案.md`。

## 10. 现场检查索引

| 顺序 | 检查动作 | 预期结果 | 证据位置 |
| --- | --- | --- | --- |
| 1 | 查看单体标签 | `monolith-start` 指向 `aba36fe` | `git tag -n`、`git show monolith-start` |
| 2 | 启动三个容器 | `db`、`web`、`nginx` 均为 healthy | `03_devops/docker-compose.yml` |
| 3 | 访问健康接口 | `live`、`ready`、`version` 均为 HTTP 200 | `http://localhost/health/ready/` |
| 4 | 运行自动化测试 | 109 项，0 失败，报告自动生成 | `04_tests/run.ps1` 或 `04_tests/tests/run_tests.py` |
| 5 | 抽查重点用例 | UC02、UC06、UC08 主成功和异常路径可验证 | `02_docs/use-case-list.md`、`04_tests/tests/` |
| 6 | 追溯一个用例 | `REQ -> UC -> 三层图 -> 代码 -> 三层测试 -> 结果` | `02_docs/追溯表.pdf` |
| 7 | 查看远程流水线 | 三平台测试、镜像、Kind 部署和健康检查均 success | GitHub Actions run `33178416274` |
| 8 | 说明微服务划分 | 3 个业务服务、11 张表唯一归属、接口与失败处理清晰 | `02_docs/微服务拆分方案.md` |

## 11. 材料路径总览

| 目录 | 检查材料 |
| --- | --- |
| `01_source` | Django 源码、模板、静态资源和依赖 |
| `02_docs` | 需求、三层设计、用例清单、追溯表、微服务方案 |
| `03_devops` | Docker、Compose、Kubernetes、数据库、部署与回滚脚本 |
| `04_tests` | 单元、集成/API、端到端测试和当前报告 |
| `05_management` | 站会记录、任务进度和管理材料 |
| `06_defense` | 答辩与演示材料目录 |

## 12. 检查结论

本项目目前满足课程中期检查要求：原单体系统可以容器化启动，核心业务用例具备自动化验证，Git 基线标签存在，需求与三层设计材料完整，CI/CD 能自动完成测试、镜像构建和部署验证，微服务拆分方案已经形成并明确接口与数据归属。

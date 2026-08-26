# Food Master 综合生活服务平台

Food Master 是基于 Django 的课程项目，覆盖账号与角色、美食外卖、团购核销、酒店预订、娱乐购票、社区博客、AI 咨询和后台治理。统一运行基线为 Python 3.10、Django 3.2.11 和 MySQL 8.0。

## 仓库结构

| 路径 | 职责 |
| --- | --- |
| `food_master/` | Django 项目配置、根路由和 WSGI 入口 |
| `myapp/` | 业务模型、视图、后台管理和数据库迁移 |
| `templates/`、`static/` | 页面模板与静态资源 |
| `tests/` | 单元、集成/API、端到端测试和测试报告 |
| `data/` | 可重复导入的演示数据库种子 |
| `docker/`、`k8s/` | 容器运行和 Kubernetes 部署清单 |
| `scripts/` | 测试、部署、回滚和课程提交打包脚本 |
| `docs/` | 需求、设计、部署、管理、追溯和提交说明 |

详细文档导航见 `docs/README.md`，协作与格式规则见 `CONTRIBUTING.md`。

## 快速启动

推荐使用 Docker Desktop 4.x 或 Docker Engine 24+ 与 Compose v2：

```powershell
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Linux/macOS 将第一行替换为 `cp .env.example .env`。首次启动会创建 MySQL 数据库、导入 `data/seed.sql`、执行迁移并收集静态文件。

- 应用入口：<http://localhost/>
- 存活检查：<http://localhost/health/live/>
- 就绪检查：<http://localhost/health/ready/>
- 版本信息：<http://localhost/health/version/>

## 本地开发

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS the_food_mas2 DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p --binary-mode the_food_mas2 < data/seed.sql
python manage.py migrate
python manage.py runserver
```

不要把真实口令写入源码。配置项见 `.env.example`；本机 `.env` 已被 Git 忽略。

演示数据中的账号仅供课程展示：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 普通用户 | `user` | `zwj1234567` |
| 骑手 | `rider001` | `hahaha233` |
| 商家 | `testShop` | `test114514` |
| 管理员 | `admin` | `quanju123` |

## 测试与格式

测试默认使用 SQLite 内存数据库，不要求本机安装 MySQL：

```powershell
.\scripts\test.ps1
python -m black --check manage.py food_master myapp tests scripts
```

Linux/macOS 使用 `./scripts/test.sh`。测试报告写入 `tests/test_report.md` 和 `tests/test_report.json`；任一失败都会阻止镜像发布与部署。完整测试说明见 `tests/README.md`。

## CI/CD

向 `main` 或 `master` 推送后，`.github/workflows/ci.yml` 自动执行：

1. Python 格式检查；
2. Windows、Ubuntu、macOS 三平台测试与部署配置检查；
3. 使用完整 Git SHA 构建并发布 GHCR 镜像；
4. 将同一镜像部署到 Kind Kubernetes 集群；
5. 验证数据库、Django、Nginx rollout 和健康接口；
6. 保存测试报告、资源快照和 Pod 日志。

部署及回滚说明见 `k8s/README.md` 和 `docs/deployment/`。

## 课程提交

`docs/submission/README.md` 记录 PDF 要求的 `01_source` 至 `06_defense` 映射。提交前运行：

```powershell
python scripts/package_submission.py --name 班级-2组-FoodMaster-软件工程基础实践
```

规范目录和同名 ZIP 会生成到已忽略的 `dist/`，不会污染代码仓库。

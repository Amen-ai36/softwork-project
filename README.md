# Food Master 综合生活服务平台

本仓库按《软件工程基础实践》最终提交要求直接采用六个一级目录。除 GitHub 必需的 `.github/`、仓库配置文件和本 README 外，项目材料全部归入以下目录。

| 目录 | 内容 |
| --- | --- |
| `01_source` | Django 源码、模板、静态资源和 Python 依赖 |
| `02_docs` | 需求、概要/详细设计、用例、追溯表和开发说明 |
| `03_devops` | Docker、GitHub Actions、Kubernetes、数据库和部署/回滚脚本 |
| `04_tests` | 单元、集成/API、端到端测试及测试报告 |
| `05_management` | 站会记录、计划、完成清单和团队管理材料 |
| `06_defense` | 答辩 PPT、技术总结和备用演示材料 |

## 快速启动

推荐使用 Docker Desktop 4.x 或 Docker Engine 24+ 与 Compose v2：

```powershell
Copy-Item 03_devops\.env.example 03_devops\.env
docker compose --env-file 03_devops\.env -f 03_devops\docker-compose.yml up -d --build
docker compose --env-file 03_devops\.env -f 03_devops\docker-compose.yml ps
```

Linux/macOS 将路径分隔符改为 `/`。首次启动会创建 MySQL 数据库、导入 `03_devops/data/seed.sql`、执行迁移并收集静态文件。

- 应用入口：<http://localhost/>
- 存活检查：<http://localhost/health/live/>
- 就绪检查：<http://localhost/health/ready/>
- 版本信息：<http://localhost/health/version/>

## 本地测试

测试默认使用 SQLite 内存数据库，无需安装 MySQL：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\04_tests\run.ps1
```

Linux/macOS 使用 `./04_tests/run.sh`。测试报告生成到 `04_tests/tests/test_report.md` 和 `04_tests/tests/test_report.json`。

## 本地开发

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r 01_source\requirements-dev.txt
Set-Location 01_source
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py runserver
```

真实口令只能放在未提交的 `03_devops/.env` 或环境变量中。开发规范见 `02_docs/development/CONTRIBUTING.md`。

## CI/CD

向 `main` 或 `master` 推送后，`.github/workflows/ci.yml` 自动执行格式检查、Windows/Ubuntu/macOS 三平台测试、版本化 GHCR 镜像构建、Kind Kubernetes 部署和健康检查。任何阶段失败都会阻止后续发布或部署。

Kubernetes 使用及回滚说明见 `03_devops/k8s/README.md`，公网和 Railway 部署说明见 `03_devops/deployment/`。

## 最终提交包

仓库本身已是六目录结构。需要生成同名压缩包时执行：

```powershell
.\.venv\Scripts\python.exe 03_devops\scripts\package_submission.py --name 班级-2组-FoodMaster-软件工程基础实践
```

结果生成到被 Git 忽略的 `dist/`。

# 开发约定

## 环境

- 使用 Python 3.10；运行依赖安装自 `01_source/requirements.txt`。
- 开发工具安装自 `01_source/requirements-dev.txt`，不要提交 `.venv/`、`.env`、IDE 用户配置或本地数据库。
- 新增配置项时同步更新 `03_devops/.env.example`，真实口令只能通过环境变量提供。

## 代码

- Python 文件使用 UTF-8、4 空格缩进和 Black 默认的 88 字符行宽。
- 模块、函数和变量使用 `snake_case`，类使用 `PascalCase`，常量使用 `UPPER_CASE`。
- 业务代码放在 `01_source/myapp/`，项目配置放在 `01_source/food_master/`，自动化测试放在 `04_tests/tests/`。
- 数据库结构变更必须生成并提交 Django migration；不要直接修改已有 migration。

提交前执行：

```powershell
python -m black --check --config 01_source/pyproject.toml 01_source/manage.py 01_source/food_master 01_source/myapp 04_tests/tests 03_devops/scripts/package_submission.py
python 04_tests/tests/run_tests.py
cd 01_source && python manage.py check --deploy --settings=food_master.test_settings
```

## 文档与提交

- 需求和设计归入 `02_docs/`，部署材料归入 `03_devops/`，管理材料归入 `05_management/`。
- 数据库初始化、容器配置和运维脚本统一归入 `03_devops/`。
- 提交信息使用明确的类型和动作，例如 `fix: handle empty cart`、`docs: update deployment guide`。
- 一个提交只处理一个主题；纯格式化与业务逻辑修改分开提交。

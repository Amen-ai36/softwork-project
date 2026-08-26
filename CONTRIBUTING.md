# 开发约定

## 环境

- 使用 Python 3.10；运行依赖安装自 `requirements.txt`。
- 开发工具安装自 `requirements-dev.txt`，不要提交 `.venv/`、`.env`、IDE 用户配置或本地数据库。
- 新增配置项时同步更新 `.env.example`，真实口令只能通过环境变量提供。

## 代码

- Python 文件使用 UTF-8、4 空格缩进和 Black 默认的 88 字符行宽。
- 模块、函数和变量使用 `snake_case`，类使用 `PascalCase`，常量使用 `UPPER_CASE`。
- 业务代码放在 `myapp/`，项目配置放在 `food_master/`，自动化测试放在 `tests/`。
- 数据库结构变更必须生成并提交 Django migration；不要直接修改已有 migration。

提交前执行：

```powershell
python -m black --check manage.py food_master myapp tests scripts
python tests/run_tests.py
python manage.py check --deploy --settings=food_master.test_settings
```

## 文档与提交

- 需求、设计、部署、管理和课程提交说明统一归入 `docs/`。
- 数据库初始化文件归入 `data/`，容器文件归入 `docker/`，运维脚本归入 `scripts/`。
- 提交信息使用明确的类型和动作，例如 `fix: handle empty cart`、`docs: update deployment guide`。
- 一个提交只处理一个主题；纯格式化与业务逻辑修改分开提交。

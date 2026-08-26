# 01_source

本目录包含 Food Master 的可运行 Django 源码。

| 路径 | 内容 |
| --- | --- |
| `food_master/` | 项目配置、根路由和 WSGI 入口 |
| `myapp/` | 业务模型、视图、后台管理和迁移 |
| `templates/`、`static/` | 页面模板和静态资源 |
| `manage.py` | Django 管理入口 |
| `requirements.txt` | 运行依赖 |
| `requirements-dev.txt`、`pyproject.toml` | 开发依赖和格式规则 |

本地运行命令应在本目录执行；跨平台一键测试请从仓库根目录调用 `04_tests/run.*`。

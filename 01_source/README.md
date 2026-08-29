# 01_source

本目录包含 Food Master 的可运行 Django 源码。

| 路径 | 内容 |
| --- | --- |
| `food_master/` | 项目配置、根路由和 WSGI 入口 |
| `myapp/` | 业务模型、视图、后台管理和迁移 |
| `services/` | `user-service`、`trade-service`、`lifestyle-service` 独立项目及共享传输契约 |
| `templates/`、`static/` | 页面模板和静态资源 |
| `manage.py` | Django 管理入口 |
| `requirements.txt` | 运行依赖 |
| `requirements-dev.txt`、`pyproject.toml` | 开发依赖和格式规则 |

`food_master/myapp` 当前作为页面与 BFF 兼容层保留；新业务接口由 `services/` 下的三个独立进程提供。跨平台一键测试请从仓库根目录调用 `04_tests/run.*`。

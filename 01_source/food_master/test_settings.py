"""
测试专用设置（供自动化测试使用）。

- 默认使用 SQLite，保证在没有 MySQL 凭据的环境（CI / 本机）也能跑通全部测试。
- 如果设置了环境变量 FOOD_DELIVER_DB_PASSWORD，则沿用生产配置使用 MySQL，
  以验证真实 MySQL 兼容性。

用法：
    PYTHONPATH=../04_tests python manage.py test tests --settings=food_master.test_settings
    或直接使用 python 04_tests/tests/run_tests.py（自动选择）。
"""

import os

from .settings import *  # noqa: F401,F403

# 测试运行环境：默认 SQLite；若提供 MySQL 密码则使用 MySQL（生产数据库配置）
if not os.environ.get("FOOD_DELIVER_DB_PASSWORD"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "test_food_master.sqlite3"),
        }
    }

# 测试时关闭外部 AI 服务依赖（llm_client 默认无 key 时返回 None，测试会 mock）
ALIYUN_API_KEY = os.environ.get("ALIYUN_API_KEY", "")  # 测试中统一走 mock

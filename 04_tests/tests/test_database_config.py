"""
数据库环境检查（配置/集成层）
==============================
目的：检查数据库配置与项目 SQL 导入文件是否一致，以及（当 MySQL 可达时）
真实数据库是否已包含项目需要的核心表。

设计：
- 纯配置断言（settings 与 03_devops/data/seed.sql 声明一致）不依赖数据库连接，始终执行。
- 真实 MySQL 表检查：如果本机没有 mysql 客户端或无法连接（如未配置密码），
  则跳过（skip），不会把"环境未配置"当成"测试失败"，避免阻塞流水线。
- 通过环境变量 FOOD_DELIVER_DB_PASSWORD 连接真实 MySQL 时可完整执行。
"""

import os
import re
import shutil
import subprocess
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "01_source"
SETTINGS_PATH = SOURCE_ROOT / "food_master" / "settings.py"
SQL_PATH = REPO_ROOT / "03_devops" / "data" / "seed.sql"
COMMON_MYSQL_PATHS = [
    Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"),
    Path(r"D:\MySQL\MySQL Server 8.0\bin\mysql.exe"),
]


def load_settings():
    spec = spec_from_file_location("food_deliver_settings", SETTINGS_PATH)
    settings = module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings


def find_mysql_client():
    from_path = shutil.which("mysql")
    if from_path:
        return from_path
    for candidate in COMMON_MYSQL_PATHS:
        if candidate.exists():
            return str(candidate)
    return None


class DatabaseConfigTest(unittest.TestCase):
    def test_settings_match_sql_dump_database(self):
        """配置一致性：settings 数据库名应与 03_devops/data/seed.sql 一致"""
        settings = load_settings()
        db = settings.DATABASES["default"]
        dump_text = SQL_PATH.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"Database:\s+([A-Za-z0-9_]+)", dump_text)

        self.assertIsNotNone(
            match, "03_devops/data/seed.sql should declare its source database"
        )
        self.assertEqual(db["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(db["NAME"], match.group(1))
        self.assertEqual(db["USER"], os.environ.get("FOOD_DELIVER_DB_USER", "root"))
        self.assertTrue(db["PASSWORD"])

    def test_settings_defaults_missing_password_are_allowed_in_tests(self):
        """配置可用性：若通过 test_settings 运行，SQLite 配置应可加载"""
        import importlib

        test_settings = importlib.import_module("food_master.test_settings")
        self.assertIn("default", test_settings.DATABASES)
        if os.environ.get("FOOD_DELIVER_DB_PASSWORD"):
            self.assertEqual(
                test_settings.DATABASES["default"]["ENGINE"], "django.db.backends.mysql"
            )
        else:
            self.assertEqual(
                test_settings.DATABASES["default"]["ENGINE"],
                "django.db.backends.sqlite3",
            )

    def test_imported_mysql_database_has_required_tables(self):
        """真实环境检查：MySQL 中存在项目核心表（无法连接时跳过）"""
        mysql = find_mysql_client()
        if not mysql:
            self.skipTest("mysql client was not found")

        settings = load_settings()
        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["MYSQL_PWD"] = db["PASSWORD"]
        result = subprocess.run(
            [
                mysql,
                "-u",
                db["USER"],
                "-h",
                db["HOST"],
                "-P",
                db["PORT"],
                db["NAME"],
                "-N",
                "-e",
                "SHOW TABLES LIKE 'myapp_%';",
            ],
            cwd=SOURCE_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            hint = result.stderr.strip()[:200]
            self.skipTest(
                f"无法连接 MySQL（{hint}）。如需检查真实库，请设置 FOOD_DELIVER_DB_PASSWORD 后重试"
            )

        tables = set(result.stdout.split())
        required_tables = {
            "myapp_user",
            "myapp_food",
            "myapp_order",
            "myapp_hotel",
            "myapp_hotelorder",
            "myapp_play",
            "myapp_playorder",
            "myapp_groupbuycoupon",
            "myapp_temp",
            "myapp_blog",
            "myapp_comment",
        }
        self.assertTrue(
            required_tables.issubset(tables),
            f"缺少表: {required_tables - tables}",
        )


if __name__ == "__main__":
    unittest.main()

import os
import re
import shutil
import subprocess
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / "src" / "food_master" / "settings.py"
SQL_PATH = ROOT / "data_hex2.sql"
COMMON_MYSQL = Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe")


def load_settings():
    spec = spec_from_file_location("food_deliver_settings", SETTINGS_PATH)
    settings = module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings


def find_mysql_client():
    from_path = shutil.which("mysql")
    if from_path:
        return from_path
    if COMMON_MYSQL.exists():
        return str(COMMON_MYSQL)
    return None


class DatabaseConfigTest(unittest.TestCase):
    def test_settings_match_sql_dump_database(self):
        settings = load_settings()
        db = settings.DATABASES["default"]
        dump_text = SQL_PATH.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"Database:\s+([A-Za-z0-9_]+)", dump_text)

        self.assertIsNotNone(match, "data_hex2.sql should declare its source database")
        self.assertEqual(db["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(db["NAME"], match.group(1))
        self.assertEqual(db["USER"], os.environ.get("FOOD_DELIVER_DB_USER", "root"))
        self.assertTrue(db["PASSWORD"])

    def test_imported_mysql_database_has_required_tables(self):
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
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
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
        }
        self.assertTrue(required_tables.issubset(tables))


if __name__ == "__main__":
    unittest.main()

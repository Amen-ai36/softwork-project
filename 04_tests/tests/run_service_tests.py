#!/usr/bin/env python
"""Run all isolated microservice API suites with portable SQLite databases."""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "01_source"
REPORT_MD = Path(__file__).with_name("microservice_test_report.md")
REPORT_JSON = Path(__file__).with_name("microservice_test_report.json")
SERVICES = (
    (
        "user-service",
        "services.user_service.config.settings",
        "services.user_service.users",
    ),
    (
        "trade-service",
        "services.trade_service.config.settings",
        "services.trade_service.trade",
    ),
    (
        "lifestyle-service",
        "services.lifestyle_service.config.settings",
        "services.lifestyle_service.lifestyle",
    ),
)


def main():
    env = dict(os.environ)
    env.update(
        {
            "SERVICE_USE_SQLITE": "true",
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8",
            "DJANGO_SECRET_KEY": "local-service-test-secret",
            "JWT_SECRET": "local-shared-jwt-test-secret",
        }
    )
    results = []
    for name, settings, tests in SERVICES:
        command = [
            sys.executable,
            "-m",
            "django",
            "test",
            tests,
            f"--settings={settings}",
            "-v",
            "2",
        ]
        print(f">> {name}: {' '.join(command)}")
        process = subprocess.run(
            command,
            cwd=SOURCE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        output = (process.stdout or "") + (process.stderr or "")
        print(output)
        match = re.search(r"Ran (\d+) tests?", output)
        results.append(
            {
                "service": name,
                "tests": int(match.group(1)) if match else 0,
                "status": "OK" if process.returncode == 0 else "FAILED",
                "returncode": process.returncode,
                "output": output,
            }
        )

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total": sum(item["tests"] for item in results),
        "status": (
            "OK" if all(item["returncode"] == 0 for item in results) else "FAILED"
        ),
        "services": results,
    }
    REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# 微服务自动化测试报告",
        "",
        f"- 生成时间：{payload['generated_at']}",
        f"- 测试总数：{payload['total']}",
        f"- 总体结果：{payload['status']}",
        "",
        "| 服务 | 测试数 | 结果 |",
        "| --- | ---: | --- |",
    ]
    for item in results:
        lines.append(f"| {item['service']} | {item['tests']} | {item['status']} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"微服务测试报告：{REPORT_MD}")
    return 0 if payload["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())

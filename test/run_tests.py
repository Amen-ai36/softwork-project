#!/usr/bin/env python
"""
统一测试入口 + 测试报告生成器
==============================
用法（项目根目录）：
    python test/run_tests.py

功能：
1. 依次运行全部自动化测试：
   - test_unit.py             单元测试（业务规则、异常分支）
   - test_integration_api.py  集成 / API 测试（主流程、备选流程、异常流程）
   - test_e2e.py              端到端测试（完整业务流程）
   - test_database_config.py  数据库配置与真实环境检查
2. 生成测试报告：
   - test/test_report.md    人读报告（总数、通过、失败、失败原因、运行环境）
   - test/test_report.json  机器可读报告
3. 测试失败时以非 0 退出码结束 —— 流水线（CI/CD）中后续发布/部署步骤
   不会继续执行。

数据库选择：
- 默认使用 SQLite（food_master/test_settings.py），无需配置即可运行；
- 设置环境变量 FOOD_DELIVER_DB_PASSWORD 后自动切换为 MySQL 真实数据库验证。
"""
import json
import os
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = Path(__file__).resolve().parent
REPORT_MD = TEST_DIR / "test_report.md"
REPORT_JSON = TEST_DIR / "test_report.json"

TEST_LABELS = [
    "test.test_unit",
    "test.test_integration_api",
    "test.test_e2e",
    "test.test_database_config",
]

DETAIL_RE = re.compile(r"^(FAIL|ERROR):\s+(.+)$")
RAN_RE = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s$", re.MULTILINE)


def configure_stdio():
    """Use UTF-8 even when the host Windows locale defaults to a legacy code page."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def detect_db_backend():
    if os.environ.get("FOOD_DELIVER_DB_PASSWORD"):
        return "MySQL（通过 FOOD_DELIVER_DB_PASSWORD 环境变量）"
    return "SQLite（food_master.test_settings）"


def collect_environment():
    import django

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "os": platform.platform(),
        "python": sys.version.split()[0],
        "django": django.get_version(),
        "db_backend": detect_db_backend(),
        "project_root": str(ROOT),
    }


def run_tests():
    settings_flag = (
        []
        if os.environ.get("FOOD_DELIVER_DB_PASSWORD")
        else ["--settings=food_master.test_settings"]
    )
    cmd = [
        sys.executable,
        "manage.py",
        "test",
        *TEST_LABELS,
        "-v",
        "2",
        *settings_flag,
    ]
    print(">> 执行命令:", " ".join(cmd))
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    return proc, (proc.stdout or "") + (proc.stderr or "")


def parse_output(output):
    """基于 Django 测试运行器的汇总输出统计（Ran N tests / OK / FAILED）"""
    reasons = []
    lines = output.splitlines()
    for i, line in enumerate(lines):
        m = DETAIL_RE.match(line)
        if not m:
            continue
        reason = ""
        for detail in lines[i + 1 : i + 60]:
            s = detail.strip()
            if not s or s.startswith(("-----", "======")):
                continue
            if re.search(
                r"(error|exception|assert|no module named|failed|expected|not found|does not exist|invalid)",
                s,
                re.I,
            ):
                reason = s[:300]
                break
        reasons.append({"test": m.group(2), "kind": m.group(1), "reason": reason or "（无详细信息）"})

    ran = RAN_RE.search(output)
    total = int(ran.group(1)) if ran else 0

    failed = errors = skipped = 0
    m_result = re.search(r"FAILED \(failures=(\d+)", output)
    if m_result:
        failed = int(m_result.group(1))
        m_err = re.search(r"errors=(\d+)", output)
        errors = int(m_err.group(1)) if m_err else 0
        m_skip = re.search(r"skipped=(\d+)", output)
        skipped = int(m_skip.group(1)) if m_skip else 0
        status = "FAILED"
    elif re.search(r"^OK", output, re.M):
        status = "OK"
        m_skip = re.search(r"OK \(skipped=(\d+)\)", output)
        skipped = int(m_skip.group(1)) if m_skip else 0
    else:
        status = "FAILED"

    passed = max(total - failed - errors - skipped, 0)
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "reasons": reasons,
        "status": status,
    }, output


def write_reports(summary, environment, output):
    md = [
        "# 自动化测试报告",
        "",
        f"- 生成时间：{environment['timestamp']}",
        f"- 运行环境：{environment['os']}",
        f"- Python：{environment['python']} / Django：{environment['django']}",
        f"- 数据库：{environment['db_backend']}",
        "",
        "## 结果汇总",
        "",
        "| 项目 | 数量 |",
        "| --- | --- |",
        f"| 测试总数 | {summary['total']} |",
        f"| 通过数 | {summary['passed']} |",
        f"| 失败数 | {summary['failed']} |",
        f"| 跳过数（环境原因） | {summary['skipped']} |",
        f"| 结果 | {summary['status']} |",
        "",
    ]
    if summary["reasons"]:
        md.append("## 失败 / 错误原因")
        md.append("")
        for item in summary["reasons"]:
            md.append(f"- **{item['kind']}** `{item['test']}`：{item['reason']}")
        md.append("")
    md.append("> 说明：任一测试失败时，`run_tests.py` 会返回非 0 退出码，")
    md.append("> CI/CD 流水线中后续的构建、发布镜像、部署步骤将不会执行。")
    md.append("")
    md.append("## 完整输出")
    md.append("")
    md.append("```text")
    md.append(output.rstrip())
    md.append("```")

    REPORT_MD.write_text("\n".join(md), encoding="utf-8")
    payload = {"environment": environment, "summary": summary}
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    configure_stdio()
    environment = collect_environment()
    proc, output = run_tests()
    summary, output = parse_output(output)
    # 兜底：进程非 0 退出（如语法错误、收集失败）也判定为失败并记录原因
    if proc.returncode != 0 and summary["status"] == "OK":
        summary["status"] = "FAILED"
        reason = "（未生成测试统计，运行进程异常退出）"
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith(("SyntaxError", "ImportError", "ModuleNotFoundError", "django.core.exceptions")):
                reason = stripped
                break
            if "Error:" in stripped and "Traceback" not in stripped:
                reason = stripped
                break
        summary["reasons"] = [{"test": "(测试收集/启动失败)", "kind": "ERROR", "reason": reason}]
        summary["failed"] += 1
    write_reports(summary, environment, output)

    print()
    print("=" * 60)
    print("测试报告已生成：")
    print(f"  {REPORT_MD}")
    print(f"  {REPORT_JSON}")
    print("-" * 60)
    print(f"总数: {summary['total']}  通过: {summary['passed']}  "
          f"失败: {summary['failed']}  跳过: {summary['skipped']}  结果: {summary['status']}")
    if summary["reasons"]:
        for item in summary["reasons"]:
            print(f"  [{item['kind']}] {item['test']}: {item['reason']}")
    print("=" * 60)

    # 失败即停：非 0 退出码（流水线据此停止发布/部署）
    return 0 if summary["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())

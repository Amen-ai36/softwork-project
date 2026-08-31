#!/usr/bin/env python
"""
统一测试入口 + 测试报告生成器
==============================
用法（项目根目录）：
    python 04_tests/tests/run_tests.py

功能：
1. 依次运行全部自动化测试：
   - test_unit.py             单元测试（业务规则、异常分支）
   - test_integration_api.py  集成 / API 测试（主流程、备选流程、异常流程）
   - test_e2e.py              端到端测试（完整业务流程）
   - test_database_config.py  数据库配置与真实环境检查
2. 生成测试报告：
   - 04_tests/tests/test_report.md    人读报告（总数、通过、失败、失败原因、运行环境）
   - 04_tests/tests/test_report.json  机器可读报告
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

from acceptance_cases import USE_CASES

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "01_source"
TEST_DIR = Path(__file__).resolve().parent
TEST_PACKAGE_ROOT = TEST_DIR.parent
REPORT_MD = TEST_DIR / "test_report.md"
REPORT_JSON = TEST_DIR / "test_report.json"
ACCEPTANCE_MD = TEST_DIR / "acceptance_report.md"
ACCEPTANCE_JSON = TEST_DIR / "acceptance_report.json"

TEST_LABELS = [
    "tests.test_unit",
    "tests.test_integration_api",
    "tests.test_e2e",
    "tests.test_database_config",
    "tests.test_devops_artifacts",
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
        "project_root": str(SOURCE_ROOT),
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
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, (str(TEST_PACKAGE_ROOT), env.get("PYTHONPATH")))
    )
    proc = subprocess.run(
        cmd,
        cwd=SOURCE_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
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
        reasons.append(
            {
                "test": m.group(2),
                "kind": m.group(1),
                "reason": reason or "（无详细信息）",
            }
        )

    ran = RAN_RE.search(output)
    total = int(ran.group(1)) if ran else 0

    failed = errors = skipped = 0
    m_result = re.search(r"^FAILED\s+\(([^)]*)\)", output, re.MULTILINE)
    if m_result:
        result_details = m_result.group(1)
        m_fail = re.search(r"failures=(\d+)", result_details)
        failed = int(m_fail.group(1)) if m_fail else 0
        m_err = re.search(r"errors=(\d+)", result_details)
        errors = int(m_err.group(1)) if m_err else 0
        m_skip = re.search(r"skipped=(\d+)", result_details)
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


def extract_test_status(output, test_id):
    test_class, method = test_id.rsplit(".", 1)
    markers = (f"{method} ({test_id})", f"{method} ({test_class})")
    starts = [output.find(marker) for marker in markers]
    starts = [start for start in starts if start >= 0]
    if not starts:
        return "MISSING"
    start = min(starts)
    remaining = output[start + len(method) :]
    next_test = re.search(r"\r?\ntest_[A-Za-z0-9_]+ \(", remaining)
    block = remaining[: next_test.start()] if next_test else remaining
    if re.search(r"\.\.\. ok\s*$", block, re.MULTILINE):
        return "PASSED"
    if re.search(r"\.\.\. skipped\b", block):
        return "SKIPPED"
    if re.search(r"\.\.\. (FAIL|ERROR)\s*$", block, re.MULTILINE):
        return "FAILED"
    return "UNKNOWN"


def build_acceptance(output):
    cases = []
    for case in USE_CASES:
        evidence = [
            {"test": test_id, "status": extract_test_status(output, test_id)}
            for test_id in case["tests"]
        ]
        cases.append(
            {
                "id": case["id"],
                "title": case["title"],
                "representative": case["representative"],
                "status": (
                    "PASSED"
                    if all(item["status"] == "PASSED" for item in evidence)
                    else "FAILED"
                ),
                "evidence": evidence,
            }
        )
    passed = sum(case["status"] == "PASSED" for case in cases)
    return {
        "total": len(cases),
        "passed": passed,
        "status": "OK" if passed == len(cases) else "FAILED",
        "cases": cases,
    }


def write_acceptance_reports(acceptance, environment):
    payload = {"generated_at": environment["timestamp"], **acceptance}
    ACCEPTANCE_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# 业务用例端到端验收报告",
        "",
        f"- 生成时间：{environment['timestamp']}",
        f"- 用例清单：UC01-UC{acceptance['total']:02d}",
        f"- 通过用例：{acceptance['passed']}/{acceptance['total']}",
        f"- 总体结果：{acceptance['status']}",
        "",
        "## 代表性用例",
        "",
        "| 用例 | 业务场景 | 自动化证据数 | 结果 |",
        "| --- | --- | ---: | --- |",
    ]
    for case in acceptance["cases"]:
        if case["representative"]:
            lines.append(
                f"| {case['id']} | {case['title']} | {len(case['evidence'])} | "
                f"{case['status']} |"
            )
    lines.extend(
        [
            "",
            "## 全部业务用例",
            "",
            "| 用例 | 业务场景 | 主流程/异常流程证据 | 结果 |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for case in acceptance["cases"]:
        lines.append(
            f"| {case['id']} | {case['title']} | {len(case['evidence'])} | "
            f"{case['status']} |"
        )
    lines.extend(["", "## 测试证据", ""])
    for case in acceptance["cases"]:
        lines.append(f"### {case['id']} {case['title']}")
        lines.append("")
        for item in case["evidence"]:
            lines.append(f"- `{item['test']}`：{item['status']}")
        lines.append("")
    ACCEPTANCE_MD.write_text("\n".join(lines), encoding="utf-8")


def write_reports(summary, environment, acceptance, output):
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
        f"| 业务用例回归 | {acceptance['passed']}/{acceptance['total']} |",
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
    payload = {
        "environment": environment,
        "summary": summary,
        "acceptance": acceptance,
    }
    REPORT_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    configure_stdio()
    environment = collect_environment()
    proc, output = run_tests()
    summary, output = parse_output(output)
    acceptance = build_acceptance(output)
    # 兜底：进程非 0 退出（如语法错误、收集失败）也判定为失败并记录原因
    if proc.returncode != 0 and summary["status"] == "OK":
        summary["status"] = "FAILED"
        reason = "（未生成测试统计，运行进程异常退出）"
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith(
                (
                    "SyntaxError",
                    "ImportError",
                    "ModuleNotFoundError",
                    "django.core.exceptions",
                )
            ):
                reason = stripped
                break
            if "Error:" in stripped and "Traceback" not in stripped:
                reason = stripped
                break
        summary["reasons"] = [
            {"test": "(测试收集/启动失败)", "kind": "ERROR", "reason": reason}
        ]
        summary["failed"] += 1
    if acceptance["status"] != "OK":
        summary["status"] = "FAILED"
        summary["reasons"].append(
            {
                "test": "UC01-UC09 端到端验收",
                "kind": "ERROR",
                "reason": "一个或多个业务用例缺少通过的自动化证据",
            }
        )
    write_reports(summary, environment, acceptance, output)
    write_acceptance_reports(acceptance, environment)

    print()
    print("=" * 60)
    print("测试报告已生成：")
    print(f"  {REPORT_MD}")
    print(f"  {REPORT_JSON}")
    print(f"  {ACCEPTANCE_MD}")
    print(f"  {ACCEPTANCE_JSON}")
    print("-" * 60)
    print(
        f"总数: {summary['total']}  通过: {summary['passed']}  "
        f"失败: {summary['failed']}  跳过: {summary['skipped']}  结果: {summary['status']}"
    )
    print(
        f"业务用例: {acceptance['passed']}/{acceptance['total']}  "
        f"结果: {acceptance['status']}"
    )
    if summary["reasons"]:
        for item in summary["reasons"]:
            print(f"  [{item['kind']}] {item['test']}: {item['reason']}")
    print("=" * 60)

    # 失败即停：非 0 退出码（流水线据此停止发布/部署）
    return 0 if summary["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())

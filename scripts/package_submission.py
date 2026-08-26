"""Build the six-directory course submission package from the current Git HEAD."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SECTION_NOTES = {
    "01_source": "项目源代码快照和仓库信息。",
    "02_docs": "需求、设计、追溯关系和测试计划。",
    "03_devops": "数据库种子、容器、CI/CD、Kubernetes 与部署脚本。",
    "04_tests": "自动化测试源码、测试报告与流水线证据。",
    "05_management": "团队计划、每日记录、完成清单和贡献材料。",
    "06_defense": "答辩演示、技术总结和备用材料。",
}


def copy_path(source, destination):
    source = ROOT / source
    if not source.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
    else:
        shutil.copy2(source, destination)


def ensure_clean_head():
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if status:
        raise SystemExit(
            "Refusing to package an uncommitted worktree. Commit changes first."
        )


def build_package(name):
    ensure_clean_head()
    DIST.mkdir(exist_ok=True)
    target = (DIST / name).resolve()
    if not target.is_relative_to(DIST.resolve()):
        raise SystemExit("Package name must resolve inside dist/.")
    if target.exists():
        shutil.rmtree(target)
    for section, note in SECTION_NOTES.items():
        section_dir = target / section
        section_dir.mkdir(parents=True)
        (section_dir / "README.md").write_text(
            f"# {section}\n\n{note}\n",
            encoding="utf-8",
        )

    subprocess.run(
        [
            "git",
            "archive",
            "--format=zip",
            f"--output={target / '01_source' / 'source.zip'}",
            "HEAD",
        ],
        cwd=ROOT,
        check=True,
    )

    copy_path("README.md", target / "02_docs" / "project-README.md")
    copy_path("docs/requirements", target / "02_docs" / "requirements")
    copy_path("docs/design", target / "02_docs" / "design")
    copy_path("docs/use-case-list.md", target / "02_docs" / "use-case-list.md")
    copy_path("docs/追溯表.pdf", target / "02_docs" / "追溯表.pdf")
    copy_path(
        "docs/project-reference.md",
        target / "02_docs" / "project-reference.md",
    )
    copy_path("tests/README.md", target / "02_docs" / "test-plan.md")

    for path in (
        ".dockerignore",
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
        "docker",
        ".github/workflows",
        "k8s",
        "scripts/deploy-k8s.sh",
        "scripts/deploy-k8s.ps1",
        "scripts/rollback-k8s.sh",
        "scripts/rollback-k8s.ps1",
        "data",
        "docs/deployment",
    ):
        copy_path(path, target / "03_devops" / path)

    copy_path("tests", target / "04_tests" / "tests")
    copy_path("docs/management", target / "05_management")
    copy_path("docs/defense", target / "06_defense")

    archive = shutil.make_archive(str(target), "zip", root_dir=DIST, base_dir=name)
    print(f"Created {target}")
    print(f"Created {archive}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        default="班级-2组-FoodMaster-软件工程基础实践",
        help="Output directory and ZIP base name under dist/.",
    )
    args = parser.parse_args()
    build_package(args.name)


if __name__ == "__main__":
    main()

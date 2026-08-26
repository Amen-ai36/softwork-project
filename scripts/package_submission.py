"""Build the six-directory course submission package from the current Git HEAD."""

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SECTIONS = (
    "01_source",
    "02_docs",
    "03_devops",
    "04_tests",
    "05_management",
    "06_defense",
)


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
        raise SystemExit("Refusing to package an uncommitted worktree. Commit changes first.")


def build_package(name):
    ensure_clean_head()
    DIST.mkdir(exist_ok=True)
    target = (DIST / name).resolve()
    if not target.is_relative_to(DIST.resolve()):
        raise SystemExit("Package name must resolve inside dist/.")
    if target.exists():
        shutil.rmtree(target)
    for section in SECTIONS:
        (target / section).mkdir(parents=True)

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

    for section in SECTIONS:
        copy_path(
            Path("submission") / section / "README.md",
            target / section / "README.md",
        )

    copy_path("README.md", target / "02_docs" / "project-README.md")
    copy_path("docs", target / "02_docs" / "docs")
    copy_path("test/README.md", target / "02_docs" / "test-plan.md")

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
        "data_hex2.sql",
        "DEPLOY.md",
        "RAILWAY.md",
    ):
        copy_path(path, target / "03_devops" / path)

    copy_path("test", target / "04_tests" / "test")
    copy_path("daily conclusion", target / "05_management" / "daily conclusion")
    copy_path("Todo.md", target / "05_management" / "Todo.md")
    copy_path("finished.md", target / "05_management" / "finished.md")
    copy_path(
        "submission/06_defense/materials",
        target / "06_defense" / "materials",
    )

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

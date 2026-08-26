"""Build the six-directory course submission package from the current Git HEAD."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
SECTIONS = (
    "01_source",
    "02_docs",
    "03_devops",
    "04_tests",
    "05_management",
    "06_defense",
)
COPY_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


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
    for section in SECTIONS:
        shutil.copytree(
            ROOT / section,
            target / section,
            ignore=COPY_IGNORE,
        )

    shutil.copy2(ROOT / "README.md", target / "02_docs" / "project-README.md")
    shutil.copytree(
        ROOT / ".github" / "workflows",
        target / "03_devops" / "github-workflows",
        dirs_exist_ok=True,
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

# 课程最终提交目录映射

依据《软件工程基础实践》任务书第 5-6 页，最终压缩包使用以下六个目录。仓库根目录继续保持可直接构建的 Django 布局；运行 `python scripts/package_submission.py --name <班级-组号-项目名-软件工程基础实践>` 会在 `dist/` 生成规范目录和同名 ZIP。

| 提交目录 | 内容 | 仓库来源 |
| --- | --- | --- |
| `01_source` | 代码或仓库清单 | 当前 Git 提交快照、仓库地址、`monolith-start` 标签 |
| `02_docs` | 需求、设计、测试、追溯和模型源文件 | `docs/`、`README.md`、用例清单 |
| `03_devops` | Docker、流水线、Kubernetes/Helm、数据库与部署脚本 | `Dockerfile`、`docker-compose.yml`、`.github/workflows/`、`k8s/`、`scripts/`、`data_hex2.sql` |
| `04_tests` | 自动化测试、压力脚本、原始报告与实验数据 | `test/`；流水线原始日志从 GitHub Actions Artifact 下载后放入此目录 |
| `05_management` | 站会简报、看板截图、贡献与权重材料 | `daily conclusion/`、`Todo.md`、`finished.md` 及团队后续补充材料 |
| `06_defense` | PPT、技术总结报告和备用演示材料 | 团队答辩材料，定稿后放入 `submission/06_defense/materials/` |

打包脚本只收集仓库中已经存在的材料，不伪造尚未完成的压力测试、看板截图、贡献权重或答辩材料。提交前需由团队负责人补齐这些课程材料，并把 GitHub Actions 的测试和 Kubernetes 部署 Artifact 下载到 `04_tests`。

# 03_devops

本目录集中保存项目交付和运维材料。

| 路径 | 内容 |
| --- | --- |
| `Dockerfile`、`docker-compose.yml` | BFF 镜像和本地多服务编排 |
| `docker/` | Nginx 配置和 Django 容器入口 |
| `services/` | 三个业务微服务共用的镜像与容器入口 |
| `k8s/` | Kustomize 清单、部署和回滚说明 |
| `data/` | MySQL 演示数据及三个 schema 的幂等初始化脚本 |
| `scripts/` | 部署、回滚和最终提交打包脚本 |
| `deployment/` | 公网与 Railway 部署说明 |

GitHub 要求工作流必须位于仓库根目录的 `.github/workflows/`，因此实际流水线文件保留在那里；生成最终提交包时会自动复制到本目录的 `github-workflows/`。

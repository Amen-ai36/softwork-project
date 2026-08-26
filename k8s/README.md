# Kubernetes 部署

`k8s/base` 使用 Kustomize 部署三个独立容器工作负载：Nginx 前端入口、Django/Gunicorn 后端和 MySQL 8 数据库。数据库使用 PVC，应用镜像由部署脚本替换为带提交 SHA 的版本号。

## 前提

- Kubernetes 1.27+；本地可使用 Docker Desktop、Kind 或 Minikube。
- `kubectl` 可访问目标集群。
- 已构建并推送版本化镜像，例如 `ghcr.io/amen-ai36/softwork-project:<commit-sha>`。

## 部署

Linux/macOS：

```bash
export DJANGO_SECRET_KEY='本地生成的随机值'
export MYSQL_ROOT_PASSWORD='本地生成的随机值'
./scripts/deploy-k8s.sh ghcr.io/amen-ai36/softwork-project:<commit-sha>
```

Windows PowerShell：

```powershell
$env:DJANGO_SECRET_KEY = '本地生成的随机值'
$env:MYSQL_ROOT_PASSWORD = '本地生成的随机值'
.\scripts\deploy-k8s.ps1 -Image ghcr.io/amen-ai36/softwork-project:<commit-sha>
```

Secret 只在首次部署时创建，不写入仓库。部署完成后可访问：

```bash
kubectl -n food-master port-forward service/food-master-nginx 8080:80
curl http://127.0.0.1:8080/health/ready/
curl http://127.0.0.1:8080/health/version/
```

云集群上 `food-master-nginx` 的 `LoadBalancer` 服务会由云平台分配外部地址。

## 回滚

```bash
./scripts/rollback-k8s.sh
```

或在 PowerShell 中执行：

```powershell
.\scripts\rollback-k8s.ps1
```

## GitHub Actions

`.github/workflows/ci.yml` 在每次向 `main`/`master` push 后自动完成：

1. 在 Ubuntu、Windows、macOS 上运行全部三层测试。
2. 测试全部通过后，构建镜像并以提交 SHA 和分支名推送到 GHCR。
3. 创建临时 Kind 集群，部署前端、后端和数据库，等待 rollout 完成。
4. 通过 Nginx 调用存活、就绪和版本接口，并上传 Kubernetes 日志与资源快照。

任一步失败都会阻止后续阶段。Kind 集群是 GitHub Runner 内的可重复部署验收环境，不是长期公网环境；长期云集群使用同一份清单和部署脚本。

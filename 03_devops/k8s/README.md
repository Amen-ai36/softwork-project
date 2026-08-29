# Kubernetes 部署

`03_devops/k8s/base` 使用 Kustomize 部署 Nginx 网关、Django BFF、三个业务微服务和 MySQL 8。数据库使用 PVC，三个业务服务分别使用独立 schema；四个应用镜像由部署脚本替换为同一提交 SHA 的精确版本。

## 前提

- Kubernetes 1.27+；本地可使用 Docker Desktop、Kind 或 Minikube。
- `kubectl` 可访问目标集群。
- 已构建并推送 `bff`、`user`、`trade`、`lifestyle` 四个版本化镜像。

## 部署

Linux/macOS：

```bash
export DJANGO_SECRET_KEY='本地生成的随机值'
export MYSQL_ROOT_PASSWORD='本地生成的随机值'
export JWT_SECRET='本地生成的随机值'
export INTERNAL_SERVICE_TOKEN='本地生成的随机值'
./03_devops/scripts/deploy-k8s.sh ghcr.io/amen-ai36/softwork-project <commit-sha>
```

Windows PowerShell：

```powershell
$env:DJANGO_SECRET_KEY = '本地生成的随机值'
$env:MYSQL_ROOT_PASSWORD = '本地生成的随机值'
$env:JWT_SECRET = '本地生成的随机值'
$env:INTERNAL_SERVICE_TOKEN = '本地生成的随机值'
.\03_devops\scripts\deploy-k8s.ps1 -ImageBase ghcr.io/amen-ai36/softwork-project -Version <commit-sha>
```

Secret 由脚本以幂等方式创建或更新，不写入仓库。部署完成后可访问：

```bash
kubectl -n food-master port-forward service/food-master-nginx 8080:80
curl http://127.0.0.1:8080/health/ready/
curl http://127.0.0.1:8080/health/version/
curl http://127.0.0.1:8080/api/users/health/ready
curl http://127.0.0.1:8080/api/trade/health/ready
curl http://127.0.0.1:8080/api/lifestyle/health/ready
```

云集群上 `food-master-nginx` 的 `LoadBalancer` 服务会由云平台分配外部地址。

## 回滚

```bash
./03_devops/scripts/rollback-k8s.sh
```

或在 PowerShell 中执行：

```powershell
.\03_devops\scripts\rollback-k8s.ps1
```

## GitHub Actions

`.github/workflows/ci.yml` 在每次向 `main`/`master` push 后自动完成：

1. 在 Ubuntu、Windows、macOS 上运行兼容层和三个微服务测试。
2. 测试全部通过后，独立构建四个镜像并以提交 SHA 和分支名推送到 GHCR。
3. 创建临时 Kind 集群，创建三个 schema，部署网关、BFF、三个服务和数据库。
4. 通过网关调用页面及所有服务的就绪和版本接口，并上传 Kubernetes 证据。

任一步失败都会阻止后续阶段。Kind 集群是 GitHub Runner 内的可重复部署验收环境，不是长期公网环境；长期云集群使用同一份清单和部署脚本。

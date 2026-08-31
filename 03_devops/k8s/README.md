# Kubernetes 部署

`03_devops/k8s/base` 使用 Kustomize 部署 Nginx 网关、Django BFF、三个业务微服务和 MySQL 8。数据库使用 PVC，三个业务服务分别使用独立 schema；四个应用镜像由部署脚本替换为同一提交 SHA 的精确版本。

## 前提

- Kubernetes 1.27+；本地可使用 Docker Desktop、Kind 或 Minikube。
- `kubectl` 可访问目标集群。
- 已构建并推送 `bff`、`user`、`trade`、`lifestyle` 四个版本化镜像。

Windows Docker Desktop 在部署、启用或重置 Kubernetes 前必须先通过代理、Registry
TLS 和集群预检；已验证配置与证书排查步骤见
[`docker/proxy-and-certificate.md`](../docker/proxy-and-certificate.md)：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  .\03_devops\scripts\check-docker-environment.ps1 -RequireKubernetes
```

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

## 日志、健康和版本

一条命令查看所有 Deployment/Pod、六个组件的最近日志，以及四个应用的存活、就绪和版本响应：

```powershell
.\03_devops\scripts\inspect-k8s.ps1
```

```bash
./03_devops/scripts/inspect-k8s.sh
```

也可以单独查看某个服务：

```bash
kubectl -n food-master logs deployment/food-master-trade --tail=200
kubectl -n food-master get pods -o wide
```

实际发生过的部署失败、日志证据、根因和修复过程见 [`02_docs/CI-CD故障排查记录.md`](../../02_docs/CI-CD故障排查记录.md)。

云集群上 `food-master-nginx` 的 `LoadBalancer` 服务会由云平台分配外部地址。

## 自动扩缩容

`base/autoscaling.yaml` 为 user、trade、lifestyle 三个业务 Deployment 配置 CPU HPA（1-3 个副本，目标 60%）。集群需要先安装 metrics-server；实验步骤、压力参数和原始数据要求见 `04_tests/performance/README.md`。

```bash
kubectl -n food-master get hpa
kubectl -n food-master get pods -l app.kubernetes.io/component=business-service -w
```

## 故障兜底

网关把 upstream 502/504 转为 HTTP 503 和 `fallback:true` JSON，避免单个业务服务故障扩散。Compose 和 Kubernetes 的停止服务演练见 `04_tests/performance/fault-injection.md`。

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

1. `01 Quality`：格式和静态检查。
2. `02 Test`：在 Ubuntu、Windows、macOS 上运行兼容层、UC01-UC09 端到端回归和三个微服务的全部公开 API 契约测试。
3. `03 Build`：独立构建四个镜像并以提交 SHA 和分支名推送到 GHCR。
4. `04 Deploy`：创建临时 Kind 集群和三个 schema，部署网关、BFF、三个服务和数据库。
5. `05 Verify`：检查存活、就绪、版本一致性，并上传 Kubernetes 日志与资源证据。

任一步失败都会阻止后续阶段。Kind 集群是 GitHub Runner 内的可重复部署验收环境，不是长期公网环境；长期云集群使用同一份清单和部署脚本。

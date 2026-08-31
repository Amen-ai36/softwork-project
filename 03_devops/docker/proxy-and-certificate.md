# Docker 代理与证书运行手册

## 本机已验证配置

记录日期：2026-08-31。

| 项目 | 已验证值 |
| --- | --- |
| Windows 系统代理 | 开启 |
| HTTP/HTTPS 代理 | `http://127.0.0.1:7897` |
| 代理进程 | Clash Verge / `verge-mihomo` |
| Docker Desktop 代理模式 | System proxy |
| Kubernetes | Docker Desktop kubeadm，验证时为 v1.36.1 |

故障发生时，Docker Desktop 的 `httpproxy.log` 明确记录
`host/Linux will use proxy: disabled`。直连 Docker Registry 触发
`x509: certificate signed by unknown authority`；恢复系统代理后日志变为
`host/Linux will use proxy: static system`，同一镜像立即可以正常拉取。因此本次根因是
Docker 未使用已配置代理，不是项目镜像损坏，也不需要关闭 TLS。

## 每次操作前的强制预检

执行 Docker 拉取/构建、启用或重置 Docker Desktop Kubernetes、部署 Kubernetes
之前，先运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  .\03_devops\scripts\check-docker-environment.ps1 -RequireKubernetes
```

仅使用 Compose、不要求 Kubernetes 时去掉 `-RequireKubernetes`。预检会验证：

1. Windows 系统代理已开启且包含 `127.0.0.1:7897`。
2. 代理端口正在监听。
3. Docker Engine 可访问。
4. Docker Desktop 已读取 static system proxy。
5. Docker Engine 可以通过代理和 TLS 拉取已知 Registry 镜像。
6. 使用 `-RequireKubernetes` 时，Kubernetes 必须处于 running 状态。

任一项失败都应先修复环境，不要继续重置集群或反复拉取镜像。

## Docker Desktop 设置

1. 先启动 Clash Verge，开启“系统代理”，确认监听地址为 `127.0.0.1:7897`。
2. 打开 Docker Desktop -> Settings -> Resources -> Proxies。
3. 优先选择 `System proxy`。若使用 Manual，HTTP 和 HTTPS 都填写
   `http://127.0.0.1:7897`。
4. Apply & Restart 后重新运行预检。

验证命令：

```powershell
docker pull docker/desktop-storage-provisioner:v4.0
docker desktop kubernetes status
kubectl get nodes
```

## 再次出现 x509 时

按以下顺序判断：

1. 检查 Clash、系统代理和 `7897` 监听端口。
2. 查看 `%LOCALAPPDATA%\Docker\log\host\httpproxy.log` 最后一条
   `will use proxy`，必须是 `static system`，不能是 `disabled`。
3. 若系统代理已正确但 Docker 日志仍为 disabled，重启 Docker Desktop。
4. 只有企业 HTTPS 中间人代理确实替换了证书链时，才把企业根 CA 导入 Windows
   Trusted Root Certification Authorities，然后重启 Docker Desktop。

`docker manifest inspect` 是 CLI 直接访问 Registry 的独立网络路径，在某些 Clash
TUN/Fake-IP 配置下可能绕过 Docker Desktop 代理；本项目以守护进程实际使用的
`docker pull` 作为预检标准。

禁止把 Registry 配置成 insecure、禁止关闭 TLS 校验、禁止把
`--kubelet-insecure-tls` 用到 Registry。当前 Metrics Server 的该参数仅用于本地
Docker Desktop kubelet 证书缺少 IP SAN 的兼容验证，与 Registry 拉取证书无关。

## 实验恢复证据

- 环境恢复记录：`04_tests/performance/results/hpa-environment-2026-08-31.md`
- HPA 实验：`04_tests/performance/results/hpa-kubeadm-2026-08-31.md`
- Kubernetes 故障隔离：`04_tests/performance/results/fault-k8s-2026-08-31.md`

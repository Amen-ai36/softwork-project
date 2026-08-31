# HPA 环境检查记录

- 日期：2026-08-31（Asia/Shanghai）
- Docker Desktop：running
- Kubernetes 模式：kind，单节点，v1.36.1

## 检查结果

`docker desktop kubernetes status` 返回：

```text
State:              failed to start
Mode:               kind
Node Count:         1
Version:            1.36.1
Progress Message:   pulling image: kindest/node:v1.36.1: exit status 1
Error:              x509: certificate signed by unknown authority
```

`kubectl config get-contexts` 没有可用 context，`kubectl cluster-info` 无法连接 API Server。由于没有集群和 Metrics Server，本次没有生成 HPA 副本变化数据，也没有把静态清单误记为实验结果。

随后按确认切换到 Docker Desktop 的 `kubeadm` 模式重试，状态变为 `failed to start`，失败点仍是 Docker Hub 证书校验：

```text
Mode:              kubeadm
Progress Message:  pulling images
Error:             pulling tag "docker/desktop-storage-provisioner:v4.0"
                    x509: certificate signed by unknown authority
```

因此切换模式本身已验证，但集群初始化仍未完成；当前没有可用于 HPA 的 API Server 或 Metrics Server。

## 后续恢复结果

确认 Clash Verge 系统代理 `127.0.0.1:7897` 开启后，同一个 `docker/desktop-storage-provisioner:v4.0` 镜像可以正常拉取。重置 kubeadm 集群后，节点进入 Ready；安装 Metrics Server v0.9.0，并仅在本地环境添加 `--kubelet-insecure-tls` 以兼容 Docker Desktop kubelet 的无 IP SAN 证书。最终 `kubectl top nodes/pods` 正常，HPA 实验完成，见 `hpa-kubeadm-2026-08-31.md`。

## 恢复步骤

1. 启动 Clash Verge 并确认系统代理为 `127.0.0.1:7897`；Docker Desktop 日志应显示 `host/Linux will use proxy: static system`。
2. 启用 Kubernetes 并确认 `kubectl get nodes` 为 Ready。
3. 安装 Metrics Server，确认 `kubectl get --raw=/apis/metrics.k8s.io/v1beta1` 成功。
4. 运行 `03_devops/scripts/run-hpa-experiment.ps1`，将脚本生成的 HPA、Pod、`kubectl top` 和压测 JSON 一并提交。

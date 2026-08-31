# 故障处理实验

网关对业务 upstream 设置 2 秒连接超时、3 秒读写超时，并把 502/504 拦截为 503 JSON：

```json
{"error":"dependency service temporarily unavailable","fallback":true}
```

这保证单个依赖服务故障只影响对应请求，其他服务仍可通过健康检查。

## Docker Compose

```powershell
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml stop trade-service
curl.exe -i http://127.0.0.1/api/trade/health/live
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml start trade-service
```

验收点：请求返回 HTTP 503 且 body 含 `fallback:true`；`user-service`、`lifestyle-service` 和 BFF 的健康检查仍为成功。

本机 Docker Desktop 的一次实际记录见 [`results/fault-compose-2026-08-31.md`](results/fault-compose-2026-08-31.md)。

## Kubernetes

```powershell
kubectl -n food-master scale deployment/food-master-trade --replicas=0
kubectl -n food-master port-forward service/food-master-nginx 8080:80
curl.exe -i http://127.0.0.1:8080/api/trade/health/live
kubectl -n food-master scale deployment/food-master-trade --replicas=1
kubectl -n food-master rollout status deployment/food-master-trade --timeout=240s
```

将停止前后的 `kubectl get pods`、网关响应和其他服务健康响应保存到实验记录；不要用截图代替命令输出和日志。

本机 kubeadm 集群的实际记录见 [`results/fault-k8s-2026-08-31.md`](results/fault-k8s-2026-08-31.md)。

HPA 实验可使用 `03_devops/scripts/run-hpa-experiment.ps1`。脚本会先检查集群和 Metrics Server，再持续压测、记录 HPA/Pod/资源指标，并等待缩容稳定窗口。本机本轮的集群证书阻塞记录见 [`results/hpa-environment-2026-08-31.md`](results/hpa-environment-2026-08-31.md)。

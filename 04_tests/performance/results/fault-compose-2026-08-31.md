# Compose 故障注入实验记录

- 日期：2026-08-31（Asia/Shanghai）
- 环境：Docker Desktop Linux engine，Compose，宿主机端口 `18080`
- 目标：停止 `trade-service`，验证故障隔离、超时与网关 fallback；其他服务保持可用

## 实验步骤

```powershell
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml -f tmp/compose.override.yml stop trade-service
curl.exe -i http://127.0.0.1:18080/api/trade/health/live
curl.exe -i http://127.0.0.1:18080/api/users/health/live
curl.exe -i http://127.0.0.1:18080/api/lifestyle/health/live
docker compose --env-file 03_devops/.env -f 03_devops/docker-compose.yml -f tmp/compose.override.yml start trade-service
```

## 实际结果

停止交易服务后，交易接口返回：

```text
HTTP/1.1 503 Service Temporarily Unavailable
Cache-Control: no-store
{"error":"dependency service temporarily unavailable","fallback":true}
```

同一时刻，其他服务返回：

```text
users:     HTTP/1.1 200 OK  {"status": "ok", "service": "user-service"}
lifestyle: HTTP/1.1 200 OK  {"status": "ok", "service": "lifestyle-service"}
```

重新启动 `trade-service` 并等待健康检查通过后，交易接口恢复：

```text
HTTP/1.1 200 OK
{"status": "ok", "service": "trade-service"}
```

## 结论

Compose 环境下已验证交易服务单点故障不会拖垮其他微服务；Nginx 会在连接失败时快速返回 503 fallback。Kubernetes 环境的同类实验仍需可用集群和 Metrics Server，见 `04_tests/performance/fault-injection.md` 与 HPA 实验脚本。

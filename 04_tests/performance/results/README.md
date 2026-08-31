# 原始实验结果

把单体和微服务每次基准运行生成的 JSON、`docker stats`/`kubectl top` 输出和实验说明放在此目录。当前目录只提交说明，不预填任何性能数字；未实际运行的数据不能用于课程报告。

## 已生成记录

- `fault-compose-2026-08-31.md`：Docker Compose 停止交易服务后的 503 fallback、其他服务 200 和恢复结果。
- `hpa-environment-2026-08-31.md`：本机 Docker Desktop Kubernetes 启动失败的证书错误和恢复步骤，未伪造副本变化数据。
- `hpa-kubeadm-2026-08-31.md`：真实 HPA 时间线，交易服务在压力下从 1 扩到 3，冷却后缩回 1。
- `fault-k8s-2026-08-31.md`：Kubernetes 中停止交易服务后的 503 隔离、其他服务 200 与恢复记录。
- `microservices-compose-2026-08-31.json`：同一交易健康接口、同一 Compose 环境下 3 次微服务网关基准，含吞吐量、平均/P95、错误率及 BFF 容器 CPU/内存采样。

单体性能对照结果仍需在对应环境完成后再放入此目录。

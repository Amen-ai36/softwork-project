# 原始实验结果

把单体和微服务每次基准运行生成的 JSON、`docker stats`/`kubectl top` 输出和实验说明放在此目录。当前目录只提交说明，不预填任何性能数字；未实际运行的数据不能用于课程报告。

## 已生成记录

- `fault-compose-2026-08-31.md`：Docker Compose 停止交易服务后的 503 fallback、其他服务 200 和恢复结果。
- `hpa-environment-2026-08-31.md`：本机 Docker Desktop Kubernetes 启动失败的证书错误和恢复步骤，未伪造副本变化数据。
- `hpa-kubeadm-2026-08-31.md`：真实 HPA 时间线，交易服务在压力下从 1 扩到 3，冷却后缩回 1。
- `fault-k8s-2026-08-31.md`：Kubernetes 中停止交易服务后的 503 隔离、其他服务 200 与恢复记录。
- `microservices-compose-2026-08-31.json`：同一交易健康接口、同一 Compose 环境下 3 次微服务网关基准，含吞吐量、平均/P95、错误率及 BFF 容器 CPU/内存采样。
- `monolith-{food,hotel,blog}-2026-09-03.json`：单体 `web` 容器（经 nginx `/` 路由）在 Docker+MySQL+gunicorn 下各 3 次的原始结果。
- `microservice-{trade-foods,lifestyle-hotels,lifestyle-blogs}-2026-09-03.json`：微服务（经 nginx `/api/*` 路由）在 Docker+MySQL+gunicorn 下各 3 次的原始结果。
- `performance-comparison-2026-09-03.md`：同一 Docker 环境下单体 vs 微服务对照报告与差异解释。

**环境说明**：2026-09-03 在 Docker Compose（MySQL 8.0 + gunicorn + nginx）下完成，单体与微服务同一环境、同一脚本、各 3 次。
此前因 Docker/MySQL 不可用的一版 SQLite + `runserver` 对照已由容器结果取代。报告中未笼统宣称“性能提升”，而是逐接口解释差异。

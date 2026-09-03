# 性能对比实验

`benchmark.py` 是单体和微服务共用的 HTTP 压测脚本。两次实验必须使用同一台机器、同一批 seed 数据、同一接口、同一并发参数，并各运行至少 3 次。脚本输出吞吐量、平均响应时间、P95、错误率和状态码；传入 `--docker-service` 时同时采样容器 CPU/内存，传入 `--host-pid` 时用 psutil 采样本地进程 CPU/内存，传入 `--cookie` 时携带会话 Cookie（用于需要登录的业务接口）。

> 已执行：**2026-09-03 容器对照**（`main` 的 BFF/单体 `web` 服务 vs user/trade/lifestyle 三微服务），
> 结果见 [`results/performance-comparison-2026-09-03.md`](results/performance-comparison-2026-09-03.md)。
> 本次在 **同一 Docker Compose + MySQL 8.0 + gunicorn + nginx** 环境、同一台机器、同一脚本、同一并发参数下，各 3 次对照。
> （此前因 Docker/MySQL 不可用曾有一版 SQLite + `runserver` 降级对照，已由容器结果取代。）

## 示例

```powershell
python 04_tests/performance/benchmark.py `
  --label monolith `
  --target http://127.0.0.1:8000 `
  --path health/ready/ `
  --requests 120 `
  --concurrency 12 `
  --runs 3 `
  --output 04_tests/performance/results/monolith.json

python 04_tests/performance/benchmark.py `
  --label microservices-gateway `
  --target http://127.0.0.1 `
  --path health/ready/ `
  --requests 120 `
  --concurrency 12 `
  --runs 3 `
  --docker-service food-master-web `
  --output 04_tests/performance/results/microservices.json
```

实际实验时把 `--path` 换成同一个主要业务接口，并在结果目录保存两个 JSON 和 `docker stats`/`kubectl top` 原始输出。不要只填写平均值；需要在报告中解释微服务版本变快或变慢的原因。

## 结果检查表（2026-09-03 已核对）

- [x] 单体与微服务使用相同接口、机器和脚本参数（美食/酒店/博客三组对照）。
- [x] 每个版本至少 3 次，已保存原始 JSON（见 `results/monolith-*-2026-09-03.json`、`results/microservice-*-2026-09-03.json`）。
- [x] 每次记录并发数、吞吐量、平均/P95、错误率、CPU、内存。
- [x] 报告注明测试时间、版本 SHA、数据库状态和环境限制（见 `results/performance-comparison-2026-09-03.md`）。

> 边界：单体和微服务虽为同一脚本/机器/并发参数、同一 Docker+MySQL+gunicorn+nginx 环境，但单体与微服务接口响应契约不同
> （HTML 页面 vs JSON API），且各接口结论不一致（美食/酒店微服务更快，博客吞吐接近）。因此报告中未笼统宣称“性能提升”，而是逐接口解释差异。

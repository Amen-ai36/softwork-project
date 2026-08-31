# 性能对比实验

`benchmark.py` 是单体和微服务共用的 HTTP 压测脚本。两次实验必须使用同一台机器、同一批 seed 数据、同一接口、同一并发参数，并各运行至少 3 次。脚本输出吞吐量、平均响应时间、P95、错误率和状态码；传入 `--docker-service` 时同时采样容器 CPU/内存。

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

## 结果检查表

- [ ] 单体与微服务使用相同接口、数据、机器和脚本参数。
- [ ] 每个版本至少 3 次，保存原始 JSON。
- [ ] 每次记录并发数、吞吐量、平均/P95、错误率、CPU、内存。
- [ ] 报告注明测试时间、版本 SHA、数据库状态和环境限制。

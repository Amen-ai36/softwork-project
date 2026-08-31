## P0 - 实验验收

- [x] 在带 Metrics Server 的 Docker Desktop kubeadm 集群应用 HPA，完成 1→3→1 扩缩容记录（`04_tests/performance/results/hpa-kubeadm-2026-08-31.md`）。
- [x] 停止 `trade-service`，保存 503 兜底响应和其他服务健康证据（Compose 与 K8s 记录均在 `04_tests/performance/results/`）。
- [ ] 按 `04_tests/performance/README.md` 对单体和微服务各运行至少 3 次，提交原始 JSON 与 CPU/内存记录。
- [ ] 清理 `seed.sql` 中的演示密码/session token；将单体用户密码改为哈希存储并轮换部署密钥。

## P1 - 回归与材料

- [ ] 增加经网关访问的微服务 UC01-UC09 端到端回归，并更新 `02_docs/traceability.md`。
- [ ] 重生成追溯 PDF 和中期报告，统一最新 Python/Django/测试数量，补交 diagrams.net/PlantUML 等模型源文件。
- [ ] 补齐 8 月 31 日至 9 月 4 日站会、看板截图、任务证据、权重确认、答辩 PPT 和技术总结。

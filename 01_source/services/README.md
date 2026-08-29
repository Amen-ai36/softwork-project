# Food Master 业务微服务

本目录按 `02_docs/微服务拆分方案.md` 实现三个可独立测试、构建、迁移和部署的 Django 服务。

| 服务 | Django settings | 默认端口 | 数据库 |
| --- | --- | ---: | --- |
| user-service | `services.user_service.config.settings` | 8001 | `user_db` |
| trade-service | `services.trade_service.config.settings` | 8002 | `trade_db` |
| lifestyle-service | `services.lifestyle_service.config.settings` | 8003 | `life_db` |

`common/` 只包含 HTTP、HS256 JWT、健康检查和 settings 工厂，不包含业务模型。三个服务共享 `JWT_SECRET`，并从令牌声明读取 `user_id` 与 `usertype`。交易和本地生活服务只保存用户裸 ID，不依赖 `user_db` 外键。

## 网关路径

- `/api/users/` -> user-service
- `/api/trade/` -> trade-service
- `/api/lifestyle/` -> lifestyle-service

每个服务提供无尾斜杠的 `health/live`、`health/ready`、`health/version`。

## 单独运行测试

在 `01_source` 目录执行：

```powershell
$env:SERVICE_USE_SQLITE = "true"
python -m django test services.user_service.users --settings=services.user_service.config.settings
python -m django test services.trade_service.trade --settings=services.trade_service.config.settings
python -m django test services.lifestyle_service.lifestyle --settings=services.lifestyle_service.config.settings
```

仓库根目录的 `04_tests/run.ps1` 或 `04_tests/run.sh` 会自动运行以上全部测试。

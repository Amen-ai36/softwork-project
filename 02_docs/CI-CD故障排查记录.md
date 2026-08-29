# CI/CD 部署故障排查记录

## 结论

- 首次失败流水线：[`33239665200`](https://github.com/Amen-ai36/softwork-project/actions/runs/33239665200)
- 失败阶段：`Deploy gateway, BFF, services, and database`
- 直接现象：数据库和 schema 初始化成功，但三个微服务长时间无法通过启动探针。
- 根因：微服务镜像已经安装 `PyMySQL`，但微服务包没有执行 `pymysql.install_as_MySQLdb()`；Django 使用 MySQL 后端执行迁移时找不到 `MySQLdb`。
- 修复提交：`a25ee6c`（在 `services/__init__.py` 注册驱动，并为三平台微服务测试增加 MySQL 驱动冒烟检查）。
- 修复后成功流水线：[`33240794134`](https://github.com/Amen-ai36/softwork-project/actions/runs/33240794134)，18/18 Jobs 成功。

## 定位过程

1. 从失败 Job 的时间分布确认镜像拉取、Kind 创建和 Secret 创建已经成功，问题发生在 Deployment 就绪等待阶段。
2. 查看资源状态：

   ```bash
   kubectl -n food-master get all,pvc -o wide
   kubectl -n food-master get events --sort-by=.lastTimestamp
   ```

3. 数据库 Pod、PVC 和 `food-master-schema-init` Job 正常，继续查看服务日志：

   ```bash
   kubectl -n food-master logs deployment/food-master-user --tail=200
   kubectl -n food-master logs deployment/food-master-trade --tail=200
   kubectl -n food-master logs deployment/food-master-lifestyle --tail=200
   ```

4. 三个日志出现相同错误：

   ```text
   django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module.
   Did you install mysqlclient?
   ModuleNotFoundError: No module named 'MySQLdb'
   ```

5. 对照原 BFF 的初始化代码后发现，BFF 已注册 `PyMySQL`，新微服务包遗漏了同一初始化。补齐后在本地 Kind 中验证三个服务完成迁移并进入 `1/1 Running`，随后远端流水线部署和网关验收全部通过。

## 防止复发

- 每个微服务在 Ubuntu、Windows、macOS 测试前执行 `import services; import MySQLdb`。
- Kubernetes 部署失败时，CI 的 `ERR` trap 会把资源、事件和六个 Deployment 的日志直接输出到 Job 页面。
- 无论成功或失败，CI 都上传 `microservices-deployment-<commit>` 证据，包含资源状态、Pod 描述、服务日志、健康与版本响应。
- 部署只使用当前提交 SHA 对应的四个镜像；版本检查不一致时流水线失败。

## 现场演示

Windows：

```powershell
.\03_devops\scripts\inspect-k8s.ps1
```

Linux/macOS：

```bash
./03_devops/scripts/inspect-k8s.sh
```

脚本会依次显示 Deployment/Pod、六个组件的最近日志，以及 BFF、用户、交易、生活服务的存活、就绪和版本响应。

# 云实验实机演示与录制运行手册

本手册用于最终答辩的两个云 Kubernetes 实验：

1. HPA 自动扩缩容
2. `trade-service` 故障处理与故障隔离

所有命令默认在仓库根目录、Windows PowerShell 中执行。命令中的 `<...>` 需要替换成实际值。

## 一次性准备

### 1. 推送代码并等待 CI/CD

如果需要在答辩中展示提交代码触发流水线，先执行：

```powershell
git status
git add .
git commit -m "prepare cloud experiment demo"
git push origin main
```

在 GitHub Actions 中等待以下阶段成功：

```text
01 Quality
02 Test
03 Build
04 Deploy
05 Verify
```

CI 中的 `04 Deploy` 是 Kind 验证集群；云集群部署仍需执行下面的 Kubernetes 部署命令。

当前仓库的镜像前缀为：

```text
ghcr.io/amen-ai36/softwork-project
```

如果使用的是 Fork 仓库，替换为：

```text
ghcr.io/<GitHub用户名>/<仓库名>
```

### 2. 连接云集群

```powershell
kubectl config get-contexts
kubectl config use-context <云集群-context名称>
kubectl config current-context
kubectl cluster-info
kubectl get nodes -o wide
```

节点状态必须为 `Ready`。

按照仓库要求，Windows 工作站执行 Kubernetes 操作前先运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\03_devops\scripts\check-docker-environment.ps1 -RequireKubernetes
```

如果预检失败，先修复 Docker、系统代理或 Kubernetes，不要继续部署。

### 3. 检查 Metrics Server

HPA 没有 Metrics Server 就不能得到有效实验结果：

```powershell
kubectl get apiservice v1beta1.metrics.k8s.io
kubectl get --raw=/apis/metrics.k8s.io/v1beta1
kubectl top nodes
```

三个命令都应正常返回。云厂商集群如果没有 Metrics Server，需要在云控制台开启监控插件，或由集群管理员按云厂商文档安装后再继续。

### 4. 部署到云集群

```powershell
$sha = (git rev-parse HEAD).Trim()

$env:DJANGO_SECRET_KEY = "demo-" + [guid]::NewGuid().ToString("N")
$env:MYSQL_ROOT_PASSWORD = "demo-" + [guid]::NewGuid().ToString("N")
$env:JWT_SECRET = "demo-" + [guid]::NewGuid().ToString("N")
$env:INTERNAL_SERVICE_TOKEN = "demo-" + [guid]::NewGuid().ToString("N")

.\03_devops\scripts\deploy-k8s.ps1 -ImageBase ghcr.io/amen-ai36/softwork-project -Version $sha
```

检查部署：

```powershell
kubectl -n food-master get deployments,pods,svc,hpa -o wide
.\03_devops\scripts\inspect-k8s.ps1
```

获取网关地址：

```powershell
kubectl -n food-master get svc food-master-nginx
```

如果云平台已分配 `EXTERNAL-IP`，可使用 `http://<EXTERNAL-IP>`。如果没有外部地址，使用端口转发：

```powershell
kubectl -n food-master port-forward service/food-master-nginx 8080:80
```

此时网关地址为：

```text
http://127.0.0.1:8080
```

录制时不要显示密钥、Token 或 Kubernetes Secret 内容。

---

## 实验一：HPA 自动扩缩容

### 实验目标

压力升高后，`trade-service` 的 Pod 从 1 个增加到 2/3 个；压力停止并等待稳定窗口后，Pod 自动回到 1 个。

### 1. 检查初始状态

```powershell
kubectl -n food-master get hpa
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide
kubectl -n food-master top pods -l app.kubernetes.io/name=food-master-trade
```

预期初始状态：

```text
当前副本数 1
最小副本数 1
最大副本数 3
CPU 目标 60%
```

### 2. 打开两个监控窗口

窗口 A，观察 HPA：

```powershell
kubectl -n food-master get hpa/food-master-trade --watch --output=wide
```

窗口 B，观察 Pod：

```powershell
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -w
```

录制时保持两个窗口都可见。

### 3. 开启网关端口

窗口 C：

```powershell
kubectl -n food-master port-forward service/food-master-nginx 18080:80
```

不要关闭此窗口。

### 4. 运行压力测试

窗口 D 执行：

```powershell
$py = if (Test-Path .\.venv\Scripts\python.exe) { ".\.venv\Scripts\python.exe" } else { "python" }

$stamp = Get-Date -Format yyyyMMdd-HHmmss
$dir = "04_tests\performance\results\hpa-live-$stamp"
New-Item -ItemType Directory -Force $dir | Out-Null

$end = (Get-Date).AddSeconds(180)
$run = 0

while ((Get-Date) -lt $end) {
    $run++
    & $py 04_tests\performance\benchmark.py --label "hpa-load-$run" --target http://127.0.0.1:18080 --path api/trade/foods --requests 2000 --concurrency 100 --runs 1 --timeout 3 --output "$dir\load-$run.json"
    if ($LASTEXITCODE -ne 0) { throw "benchmark failed" }
}
```

压力过程中，窗口 A 应看到 CPU 超过目标并出现副本变化，例如：

```text
food-master-trade  cpu: 846%/60%  1  3  1
food-master-trade  cpu: 855%/60%  1  3  2
food-master-trade  cpu: .../60%  1  3  3
```

窗口 B 应看到：

```text
1 个 Running Pod
2 个 Running Pod
3 个 Running Pod
```

不要在压力还未结束时手动缩容。

### 5. 等待自动缩容

压力脚本结束后保持窗口 A、B 开启，等待至少 180 秒：

```powershell
Start-Sleep -Seconds 180
kubectl -n food-master get hpa/food-master-trade -o wide
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide
kubectl -n food-master top pods -l app.kubernetes.io/name=food-master-trade
```

预期最终结果：

```text
副本数：1
CPU：回到低值
Pod：1 个 Running
```

### 6. 展示性能结果

压力结果保存在刚才生成的目录中：

```powershell
Get-ChildItem $dir
Get-Content "$dir\load-1.json"
```

PPT 或视频中展示以下字段：
ss
```text
throughput_rps       吞吐量
average_ms           平均响应时间
p95_ms               P95 响应时间
error_rate           错误率
successful           成功请求数
```

仓库已有一次真实结果，可作为数量级参考：

```text
吞吐量：209.859 req/s
平均响应时间：392.281 ms
P95：804.216 ms
错误率：0
Pod：1 → 2 → 3 → 1
```

也可以使用自动记录脚本生成完整 Markdown 证据：

```powershell
.\03_devops\scripts\run-hpa-experiment.ps1 -BenchmarkPath "api/trade/foods" -LoadSeconds 180 -CooldownSeconds 180 -RequestsPerRun 2000 -Concurrency 100 -Output "04_tests\performance\results\hpa-live.md"
```

自动脚本会保存 HPA、Pod、Metrics Server 和压测 JSON。使用自动脚本时，不要再同时占用它的 `18080` 端口。

---

## 实验二：故障处理与故障隔离

### 实验目标

停止 `trade-service`，验证交易路由返回预设降级结果，而用户服务、本地生活服务和 BFF 仍保持可用。

### 1. 确认正常状态

确保端口转发窗口仍在运行，然后执行：

```powershell
curl.exe -i http://127.0.0.1:8080/api/trade/health/live
curl.exe -i http://127.0.0.1:8080/api/users/health/live
curl.exe -i http://127.0.0.1:8080/api/lifestyle/health/live
curl.exe -i http://127.0.0.1:8080/health/ready/
```

预期全部为 `HTTP 200`。

检查交易 Pod：

```powershell
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide
```

### 2. 暂停 HPA 对交易服务的自动控制

如果直接把 Deployment 缩容到 0，HPA 可能自动恢复副本。因此先临时把 HPA 指向一个不存在的目标：

```powershell
kubectl -n food-master patch hpa food-master-trade --type=merge -p '{"spec":{"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"food-master-trade-paused"}}}'
```

### 3. 停止交易服务

```powershell
kubectl -n food-master scale deployment/food-master-trade --replicas=0
kubectl -n food-master wait --for=delete pod -l app.kubernetes.io/name=food-master-trade --timeout=120s
kubectl -n food-master get deployment/food-master-trade
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade
```

录制画面中应看到交易服务副本数为 0、没有 Running 的交易 Pod。

### 4. 验证交易路由降级

```powershell
curl.exe -i http://127.0.0.1:8080/api/trade/health/live
```

预期结果：

```text
HTTP/1.1 503 Service Temporarily Unavailable

{"error":"dependency service temporarily unavailable","fallback":true}
```

必须把 HTTP 状态码和 `fallback:true` 录清楚。

### 5. 验证其他服务没有受到影响

```powershell
curl.exe -i http://127.0.0.1:8080/api/users/health/live
curl.exe -i http://127.0.0.1:8080/api/lifestyle/health/live
curl.exe -i http://127.0.0.1:8080/health/ready/
```

预期结果：

```text
user-service：HTTP 200
lifestyle-service：HTTP 200
BFF：HTTP 200
```

可选地查看网关日志：

```powershell
kubectl -n food-master logs deployment/food-master-nginx --tail=50
```

### 6. 恢复交易服务和 HPA

```powershell
kubectl -n food-master scale deployment/food-master-trade --replicas=1
kubectl -n food-master rollout status deployment/food-master-trade --timeout=240s
kubectl -n food-master patch hpa food-master-trade --type=merge -p '{"spec":{"scaleTargetRef":{"apiVersion":"apps/v1","kind":"Deployment","name":"food-master-trade"}}}'
```

确认服务已经恢复：

```powershell
curl.exe -i http://127.0.0.1:8080/api/trade/health/live
kubectl -n food-master get hpa/food-master-trade -o wide
kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide
```

预期：

```text
trade-service：HTTP 200
Pod：1 个 Running
HPA 目标：Deployment/food-master-trade
```

实验结束后必须确认 HPA 不再指向 `food-master-trade-paused`。

---

## 推荐录制顺序

### HPA 视频

```text
初始 HPA/POD 状态
→ 开始压测
→ CPU 超过 60%
→ Pod 1→2→3
→ 压测结束
→ 等待冷却
→ Pod 回到 1
→ 展示性能 JSON
```

### 故障视频

```text
所有接口 HTTP 200
→ HPA 临时暂停
→ trade-service 缩容到 0
→ trade 接口 HTTP 503 + fallback:true
→ users/lifestyle/BFF 仍为 HTTP 200
→ 恢复 trade-service
→ trade 接口回到 HTTP 200
```

建议使用屏幕录制软件，同时保留命令窗口和输出。可以加配音说明：

```text
本实验验证 CPU 型 HPA 的扩容和缩容闭环。
压力期间交易服务副本数增加，压力停止后经过稳定窗口恢复到最小副本数。

现在停止交易服务，验证网关是否返回预设降级结果。
交易请求返回 503 fallback，但用户服务、本地生活服务和 BFF 仍返回 200，说明故障被隔离。
```

---

## 相关仓库文件

- `03_devops/scripts/deploy-k8s.ps1`：Kubernetes 部署脚本
- `03_devops/scripts/run-hpa-experiment.ps1`：HPA 自动实验及证据记录脚本
- `04_tests/performance/benchmark.py`：压测脚本
- `04_tests/performance/fault-injection.md`：故障注入说明
- `04_tests/performance/results/hpa-kubeadm-2026-08-31.md`：已有 HPA 真实记录
- `04_tests/performance/results/fault-k8s-2026-08-31.md`：已有故障隔离真实记录

已有 MP4 只能作为备用素材，不能替代本次实机命令、配置和日志证据。


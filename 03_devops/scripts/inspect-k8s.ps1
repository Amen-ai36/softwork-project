param(
    [string]$Namespace = "food-master",
    [int]$TailLines = 100
)

$ErrorActionPreference = "Stop"
$Components = @("db", "web", "user", "trade", "lifestyle", "nginx")
$ProbePaths = @(
    "/health/live/",
    "/health/ready/",
    "/health/version/",
    "/api/users/health/live",
    "/api/users/health/ready",
    "/api/users/health/version",
    "/api/trade/health/live",
    "/api/trade/health/ready",
    "/api/trade/health/version",
    "/api/lifestyle/health/live",
    "/api/lifestyle/health/ready",
    "/api/lifestyle/health/version"
)

Write-Host "== Workloads =="
kubectl -n $Namespace get deployments,pods -o wide

foreach ($Component in $Components) {
    Write-Host "`n== $Component logs (last $TailLines lines) =="
    kubectl -n $Namespace logs "deployment/food-master-$Component" --tail=$TailLines
}

Write-Host "`n== Gateway probes =="
foreach ($Path in $ProbePaths) {
    Write-Host "[$Path]"
    kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- "http://127.0.0.1$Path"
}

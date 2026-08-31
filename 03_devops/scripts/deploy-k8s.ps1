param(
    [Parameter(Mandatory = $true)]
    [string]$ImageBase,
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = "Stop"
$Namespace = "food-master"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

kubectl apply -f (Join-Path $ProjectRoot "k8s\base\namespace.yaml")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $env:DJANGO_SECRET_KEY -or -not $env:MYSQL_ROOT_PASSWORD -or -not $env:JWT_SECRET -or -not $env:INTERNAL_SERVICE_TOKEN) {
    throw "Set DJANGO_SECRET_KEY, MYSQL_ROOT_PASSWORD, JWT_SECRET, and INTERNAL_SERVICE_TOKEN before deployment."
}
kubectl -n $Namespace create secret generic food-master-secrets `
    --from-literal="DJANGO_SECRET_KEY=$env:DJANGO_SECRET_KEY" `
    --from-literal="MYSQL_ROOT_PASSWORD=$env:MYSQL_ROOT_PASSWORD" `
    --from-literal="FOOD_DELIVER_DB_PASSWORD=$env:MYSQL_ROOT_PASSWORD" `
    --from-literal="JWT_SECRET=$env:JWT_SECRET" `
    --from-literal="INTERNAL_SERVICE_TOKEN=$env:INTERNAL_SERVICE_TOKEN" `
    --dry-run=client -o yaml | kubectl apply -f -
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

kubectl apply -k (Join-Path $ProjectRoot "k8s\base")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace set image deployment/food-master-web "web=$ImageBase-bff`:$Version"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace set image deployment/food-master-user "user-service=$ImageBase-user`:$Version"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace set image deployment/food-master-trade "trade-service=$ImageBase-trade`:$Version"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace set image deployment/food-master-lifestyle "lifestyle-service=$ImageBase-lifestyle`:$Version"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($Deployment in @("food-master-web", "food-master-user", "food-master-trade", "food-master-lifestyle")) {
    kubectl -n $Namespace set env "deployment/$Deployment" "APP_VERSION=$Version"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
kubectl -n $Namespace rollout status deployment/food-master-db --timeout=240s
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace wait --for=condition=complete job/food-master-schema-init --timeout=240s
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
foreach ($Deployment in @("food-master-web", "food-master-user", "food-master-trade", "food-master-lifestyle", "food-master-nginx")) {
    $Timeout = if ($Deployment -eq "food-master-web") { "360s" } elseif ($Deployment -eq "food-master-nginx") { "180s" } else { "240s" }
    kubectl -n $Namespace rollout status "deployment/$Deployment" "--timeout=$Timeout"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
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
foreach ($Path in $ProbePaths) {
    kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- "http://127.0.0.1$Path"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

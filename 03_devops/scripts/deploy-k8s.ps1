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
kubectl -n $Namespace set image deployment/food-master-user "user-service=$ImageBase-user`:$Version"
kubectl -n $Namespace set image deployment/food-master-trade "trade-service=$ImageBase-trade`:$Version"
kubectl -n $Namespace set image deployment/food-master-lifestyle "lifestyle-service=$ImageBase-lifestyle`:$Version"
foreach ($Deployment in @("food-master-web", "food-master-user", "food-master-trade", "food-master-lifestyle")) {
    kubectl -n $Namespace set env "deployment/$Deployment" "APP_VERSION=$Version"
}
kubectl -n $Namespace rollout status deployment/food-master-db --timeout=240s
kubectl -n $Namespace wait --for=condition=complete job/food-master-schema-init --timeout=240s
kubectl -n $Namespace rollout status deployment/food-master-web --timeout=360s
kubectl -n $Namespace rollout status deployment/food-master-user --timeout=240s
kubectl -n $Namespace rollout status deployment/food-master-trade --timeout=240s
kubectl -n $Namespace rollout status deployment/food-master-lifestyle --timeout=240s
kubectl -n $Namespace rollout status deployment/food-master-nginx --timeout=180s
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/health/ready/
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/api/users/health/ready
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/api/trade/health/ready
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/api/lifestyle/health/ready

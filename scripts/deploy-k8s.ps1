param(
    [Parameter(Mandatory = $true)]
    [string]$Image
)

$ErrorActionPreference = "Stop"
$Namespace = "food-master"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

kubectl apply -f (Join-Path $ProjectRoot "k8s\base\namespace.yaml")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

kubectl -n $Namespace get secret food-master-secrets 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    if (-not $env:DJANGO_SECRET_KEY -or -not $env:MYSQL_ROOT_PASSWORD) {
        throw "Set DJANGO_SECRET_KEY and MYSQL_ROOT_PASSWORD before the first deployment."
    }
    kubectl -n $Namespace create secret generic food-master-secrets `
        --from-literal="DJANGO_SECRET_KEY=$env:DJANGO_SECRET_KEY" `
        --from-literal="MYSQL_ROOT_PASSWORD=$env:MYSQL_ROOT_PASSWORD" `
        --from-literal="FOOD_DELIVER_DB_PASSWORD=$env:MYSQL_ROOT_PASSWORD"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

kubectl apply -k (Join-Path $ProjectRoot "k8s\base")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace set image deployment/food-master-web "web=$Image"
kubectl -n $Namespace set env deployment/food-master-web "APP_VERSION=$($Image.Split(':')[-1])"
kubectl -n $Namespace rollout status deployment/food-master-db --timeout=240s
kubectl -n $Namespace rollout status deployment/food-master-web --timeout=360s
kubectl -n $Namespace rollout status deployment/food-master-nginx --timeout=180s
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/health/ready/

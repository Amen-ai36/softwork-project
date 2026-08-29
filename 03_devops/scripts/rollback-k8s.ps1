$ErrorActionPreference = "Stop"
$Namespace = "food-master"

foreach ($Deployment in @("food-master-web", "food-master-user", "food-master-trade", "food-master-lifestyle")) {
    kubectl -n $Namespace rollout undo "deployment/$Deployment"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
foreach ($Deployment in @("food-master-web", "food-master-user", "food-master-trade", "food-master-lifestyle")) {
    kubectl -n $Namespace rollout status "deployment/$Deployment" --timeout=360s
}
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/health/version/

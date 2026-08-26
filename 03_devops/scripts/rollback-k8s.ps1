$ErrorActionPreference = "Stop"
$Namespace = "food-master"

kubectl -n $Namespace rollout undo deployment/food-master-web
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
kubectl -n $Namespace rollout status deployment/food-master-web --timeout=360s
kubectl -n $Namespace exec deployment/food-master-nginx -- wget -qO- http://127.0.0.1/health/version/

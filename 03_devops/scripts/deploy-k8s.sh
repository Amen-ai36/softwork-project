#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <versioned-image>" >&2
  exit 2
fi

IMAGE="$1"
NAMESPACE="food-master"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

kubectl apply -f "$PROJECT_ROOT/k8s/base/namespace.yaml"

if ! kubectl -n "$NAMESPACE" get secret food-master-secrets >/dev/null 2>&1; then
  : "${DJANGO_SECRET_KEY:?Set DJANGO_SECRET_KEY before the first deployment}"
  : "${MYSQL_ROOT_PASSWORD:?Set MYSQL_ROOT_PASSWORD before the first deployment}"
  kubectl -n "$NAMESPACE" create secret generic food-master-secrets \
    --from-literal="DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" \
    --from-literal="MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" \
    --from-literal="FOOD_DELIVER_DB_PASSWORD=$MYSQL_ROOT_PASSWORD"
fi

kubectl apply -k "$PROJECT_ROOT/k8s/base"
kubectl -n "$NAMESPACE" set image deployment/food-master-web "web=$IMAGE"
kubectl -n "$NAMESPACE" set env deployment/food-master-web "APP_VERSION=${IMAGE##*:}"
kubectl -n "$NAMESPACE" rollout status deployment/food-master-db --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-web --timeout=360s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-nginx --timeout=180s
kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
  wget -qO- http://127.0.0.1/health/ready/

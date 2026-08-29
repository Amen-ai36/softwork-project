#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <registry-base> <version>" >&2
  exit 2
fi

IMAGE_BASE="${1%/}"
VERSION="$2"
NAMESPACE="food-master"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

kubectl apply -f "$PROJECT_ROOT/k8s/base/namespace.yaml"

: "${DJANGO_SECRET_KEY:?Set DJANGO_SECRET_KEY before deployment}"
: "${MYSQL_ROOT_PASSWORD:?Set MYSQL_ROOT_PASSWORD before deployment}"
: "${JWT_SECRET:?Set JWT_SECRET before deployment}"
: "${INTERNAL_SERVICE_TOKEN:?Set INTERNAL_SERVICE_TOKEN before deployment}"
kubectl -n "$NAMESPACE" create secret generic food-master-secrets \
  --from-literal="DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY" \
  --from-literal="MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD" \
  --from-literal="FOOD_DELIVER_DB_PASSWORD=$MYSQL_ROOT_PASSWORD" \
  --from-literal="JWT_SECRET=$JWT_SECRET" \
  --from-literal="INTERNAL_SERVICE_TOKEN=$INTERNAL_SERVICE_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -k "$PROJECT_ROOT/k8s/base"
kubectl -n "$NAMESPACE" set image deployment/food-master-web "web=$IMAGE_BASE-bff:$VERSION"
kubectl -n "$NAMESPACE" set image deployment/food-master-user "user-service=$IMAGE_BASE-user:$VERSION"
kubectl -n "$NAMESPACE" set image deployment/food-master-trade "trade-service=$IMAGE_BASE-trade:$VERSION"
kubectl -n "$NAMESPACE" set image deployment/food-master-lifestyle "lifestyle-service=$IMAGE_BASE-lifestyle:$VERSION"
for deployment in food-master-web food-master-user food-master-trade food-master-lifestyle; do
  kubectl -n "$NAMESPACE" set env "deployment/$deployment" "APP_VERSION=$VERSION"
done
kubectl -n "$NAMESPACE" rollout status deployment/food-master-db --timeout=240s
kubectl -n "$NAMESPACE" wait --for=condition=complete job/food-master-schema-init --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-web --timeout=360s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-user --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-trade --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-lifestyle --timeout=240s
kubectl -n "$NAMESPACE" rollout status deployment/food-master-nginx --timeout=180s
kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
  wget -qO- http://127.0.0.1/health/ready/
for service in users trade lifestyle; do
  kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
    wget -qO- "http://127.0.0.1/api/$service/health/ready"
done

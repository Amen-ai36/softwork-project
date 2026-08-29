#!/bin/sh
set -eu

NAMESPACE="food-master"
for deployment in food-master-web food-master-user food-master-trade food-master-lifestyle; do
  kubectl -n "$NAMESPACE" rollout undo "deployment/$deployment"
done
for deployment in food-master-web food-master-user food-master-trade food-master-lifestyle; do
  kubectl -n "$NAMESPACE" rollout status "deployment/$deployment" --timeout=360s
done
kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
  wget -qO- http://127.0.0.1/health/version/

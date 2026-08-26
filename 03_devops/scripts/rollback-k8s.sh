#!/bin/sh
set -eu

NAMESPACE="food-master"
kubectl -n "$NAMESPACE" rollout undo deployment/food-master-web
kubectl -n "$NAMESPACE" rollout status deployment/food-master-web --timeout=360s
kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
  wget -qO- http://127.0.0.1/health/version/

#!/bin/sh
set -eu

NAMESPACE="${1:-food-master}"
TAIL_LINES="${LOG_TAIL:-100}"
COMPONENTS="db web user trade lifestyle nginx"
PROBES="live ready version"

echo "== Workloads =="
kubectl -n "$NAMESPACE" get deployments,pods -o wide

for component in $COMPONENTS; do
  echo
  echo "== $component logs (last $TAIL_LINES lines) =="
  kubectl -n "$NAMESPACE" logs "deployment/food-master-$component" \
    --tail="$TAIL_LINES"
done

echo
echo "== Gateway probes =="
for probe in $PROBES; do
  echo "[/health/$probe/]"
  kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
    wget -qO- "http://127.0.0.1/health/$probe/"
done
for service in users trade lifestyle; do
  for probe in $PROBES; do
    echo "[/api/$service/health/$probe]"
    kubectl -n "$NAMESPACE" exec deployment/food-master-nginx -- \
      wget -qO- "http://127.0.0.1/api/$service/health/$probe"
  done
done

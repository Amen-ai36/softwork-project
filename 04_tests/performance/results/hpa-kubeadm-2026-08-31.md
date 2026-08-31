# HPA experiment record

- Time: 2026-08-31T15:15:45.6556289+08:00
- Namespace: food-master
- Deployment: food-master-trade
- Load endpoint: /api/trade/foods
- Load duration: 120 seconds
- Cooldown: 180 seconds

## cluster access

kubectl version --request-timeout=5s

```text
Client Version: v1.36.1
Kustomize Version: v5.8.1
Server Version: v1.36.1
```

## metrics-server availability

kubectl get --raw=/apis/metrics.k8s.io/v1beta1

```text
{"kind":"APIResourceList","apiVersion":"v1","groupVersion":"metrics.k8s.io/v1beta1","resources":[{"name":"nodes","singularName":"","namespaced":false,"kind":"NodeMetrics","verbs":["get","list"]},{"name":"pods","singularName":"","namespaced":true,"kind":"PodMetrics","verbs":["get","list"]}]}
```

## initial HPA and pods

kubectl -n food-master get hpa,pods -o wide

```text
NAME                                                        REFERENCE                          TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
horizontalpodautoscaler.autoscaling/food-master-lifestyle   Deployment/food-master-lifestyle   cpu: 2%/60%   1         3         1          16m
horizontalpodautoscaler.autoscaling/food-master-trade       Deployment/food-master-trade       cpu: 2%/60%   1         3         1          16m
horizontalpodautoscaler.autoscaling/food-master-user        Deployment/food-master-user        cpu: 2%/60%   1         3         1          16m

NAME                                         READY   STATUS      RESTARTS   AGE     IP          NODE             NOMINATED NODE   READINESS GATES
pod/food-master-db-576d67c5c9-fzfpf          1/1     Running     0          16m     10.1.0.8    docker-desktop   <none>           <none>
pod/food-master-lifestyle-6c745fc8bd-k4v89   1/1     Running     0          5m57s   10.1.0.26   docker-desktop   <none>           <none>
pod/food-master-nginx-d778df758-r4lrr        1/1     Running     0          16m     10.1.0.11   docker-desktop   <none>           <none>
pod/food-master-schema-init-5bcr2            0/1     Completed   0          16m     10.1.0.12   docker-desktop   <none>           <none>
pod/food-master-trade-578b7c7568-9lq58       1/1     Running     0          5m57s   10.1.0.25   docker-desktop   <none>           <none>
pod/food-master-user-74886c8c5d-lgp8n        1/1     Running     0          5m57s   10.1.0.24   docker-desktop   <none>           <none>
pod/food-master-web-6986588964-9hvtd         1/1     Running     0          5m58s   10.1.0.23   docker-desktop   <none>           <none>
```

## initial metrics

kubectl -n food-master top pods

```text
NAME                                     CPU(cores)   MEMORY(bytes)
food-master-db-576d67c5c9-fzfpf          7m           524Mi
food-master-lifestyle-6c745fc8bd-k4v89   1m           75Mi
food-master-nginx-d778df758-r4lrr        1m           25Mi
food-master-trade-578b7c7568-9lq58       1m           75Mi
food-master-user-74886c8c5d-lgp8n        1m           74Mi
food-master-web-6986588964-9hvtd         2m           156Mi
```

## sustained load

The benchmark runs repeatedly for 120 seconds with concurrency=100.


## HPA state after load


## HPA after load

kubectl -n food-master get hpa/food-master-trade -o wide

```text
NAME                REFERENCE                      TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
food-master-trade   Deployment/food-master-trade   cpu: 855%/60%   1         3         2          18m
```

## pods after load

kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide

```text
NAME                                 READY   STATUS    RESTARTS   AGE    IP          NODE             NOMINATED NODE   READINESS GATES
food-master-trade-578b7c7568-86v2q   1/1     Running   0          32s    10.1.0.28   docker-desktop   <none>           <none>
food-master-trade-578b7c7568-9lq58   1/1     Running   0          8m1s   10.1.0.25   docker-desktop   <none>           <none>
food-master-trade-578b7c7568-qvkld   1/1     Running   0          92s    10.1.0.27   docker-desktop   <none>           <none>
```

## metrics after load

kubectl -n food-master top pods -l app.kubernetes.io/name=food-master-trade

```text
NAME                                 CPU(cores)   MEMORY(bytes)
food-master-trade-578b7c7568-86v2q   6m           73Mi
food-master-trade-578b7c7568-9lq58   1m           76Mi
food-master-trade-578b7c7568-qvkld   1m           76Mi
```

## cooldown

Waiting 180 seconds for scale-down stabilization.


## HPA after cooldown

kubectl -n food-master get hpa/food-master-trade -o wide

```text
NAME                REFERENCE                      TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
food-master-trade   Deployment/food-master-trade   cpu: 2%/60%   1         3         1          21m
```

## pods after cooldown

kubectl -n food-master get pods -l app.kubernetes.io/name=food-master-trade -o wide

```text
NAME                                 READY   STATUS    RESTARTS   AGE   IP          NODE             NOMINATED NODE   READINESS GATES
food-master-trade-578b7c7568-9lq58   1/1     Running   0          11m   10.1.0.25   docker-desktop   <none>           <none>
```

## HPA watch output

```text
NAME                REFERENCE                      TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
food-master-trade   Deployment/food-master-trade   cpu: 2%/60%   1         3         1          16m
food-master-trade   Deployment/food-master-trade   cpu: 846%/60%   1         3         1          17m
food-master-trade   Deployment/food-master-trade   cpu: 855%/60%   1         3         2          18m
food-master-trade   Deployment/food-master-trade   cpu: 2%/60%     1         3         3          19m
food-master-trade   Deployment/food-master-trade   cpu: 2%/60%     1         3         3          20m
food-master-trade   Deployment/food-master-trade   cpu: 2%/60%     1         3         1          21m
```

## port-forward stderr

```text
```

## acceptance

Expected: replicas increase above 1 during sustained load and return to 1 after cooldown; record the observed values in the submission report.

## observed result

- Initial state: 1 replica at `2%/60%` CPU.
- Under load: CPU reached `846%/60%` and then `855%/60%`; the Deployment grew from 1 to 2 and then 3 Ready Pods.
- After cooldown: CPU returned to `2%/60%` and the Deployment returned to 1 Pod.
- Acceptance result: PASS.

The first seven load batches completed 14,000/14,000 requests successfully. Later batches exhausted the Windows host load generator's short-lived connection capacity and contain `network_error` results; Kubernetes Pods and the Nginx route remained healthy. Those raw files are retained as an environment limitation and are not used as application performance results.

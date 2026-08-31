# Repository Agent Instructions

- Before any Docker pull/build, Docker Desktop Kubernetes enable/reset, or Kubernetes deployment on this Windows workstation, run:
  `powershell -NoProfile -ExecutionPolicy Bypass -File .\03_devops\scripts\check-docker-environment.ps1 -RequireKubernetes`
- The expected local system proxy is `127.0.0.1:7897`. If the preflight fails, stop and fix the proxy or restart Docker Desktop before retrying.
- Never solve registry `x509` failures by disabling TLS, adding an insecure registry, or suppressing certificate verification. Follow `03_devops/docker/proxy-and-certificate.md`.
- The local Metrics Server `--kubelet-insecure-tls` compatibility flag is limited to Docker Desktop kubelet metrics and must not be treated as a Docker Registry certificate workaround.
- For new raster-image generation, use the installed `zhumeng-imagegen` skill and its configured Zhumeng `gpt-image-2` provider by default. Use another provider only when explicitly requested, or for image editing and operations unsupported by the generation-only skill.

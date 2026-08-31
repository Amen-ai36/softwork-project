from pathlib import Path

from django.test import SimpleTestCase

REPO_ROOT = Path(__file__).resolve().parents[2]


class DevOpsArtifactTest(SimpleTestCase):
    def test_hpa_is_declared_for_all_business_services(self):
        manifest = (REPO_ROOT / "03_devops/k8s/base/autoscaling.yaml").read_text(
            encoding="utf-8"
        )
        self.assertEqual(manifest.count("kind: HorizontalPodAutoscaler"), 3)
        self.assertEqual(manifest.count("apiVersion: autoscaling/v2"), 3)
        self.assertEqual(manifest.count("averageUtilization: 60"), 3)
        self.assertEqual(manifest.count("stabilizationWindowSeconds: 120"), 3)
        for deployment in ("user", "trade", "lifestyle"):
            self.assertIn(f"name: food-master-{deployment}", manifest)
        kustomization = (REPO_ROOT / "03_devops/k8s/base/kustomization.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("autoscaling.yaml", kustomization)

    def test_gateway_has_timeout_and_fallback_configuration(self):
        for relative_path in (
            "03_devops/docker/nginx.conf",
            "03_devops/k8s/base/nginx.yaml",
        ):
            content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("proxy_intercept_errors on", content)
            self.assertRegex(content, r"proxy_(connect|read|send)_timeout")
            self.assertIn("fallback", content)
            self.assertIn("return 503", content)

    def test_performance_and_fault_runbooks_are_committed(self):
        benchmark = REPO_ROOT / "04_tests/performance/benchmark.py"
        self.assertTrue(benchmark.is_file())
        content = benchmark.read_text(encoding="utf-8")
        for metric in ("throughput_rps", "average_ms", "p95_ms", "error_rate"):
            self.assertIn(metric, content)
        self.assertTrue(
            (REPO_ROOT / "04_tests/performance/fault-injection.md").is_file()
        )
        hpa_script = REPO_ROOT / "03_devops/scripts/run-hpa-experiment.ps1"
        self.assertTrue(hpa_script.is_file())
        hpa_script_content = hpa_script.read_text(encoding="utf-8")
        self.assertIn("metrics-server availability", hpa_script_content)
        self.assertIn("CooldownSeconds", hpa_script_content)

    def test_kubernetes_deploy_stops_when_kubectl_fails(self):
        content = (REPO_ROOT / "03_devops/scripts/deploy-k8s.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'kubectl -n $Namespace rollout status "deployment/$Deployment" '
            '"--timeout=$Timeout"\n'
            "    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }",
            content,
        )
        self.assertIn(
            "kubectl -n $Namespace wait --for=condition=complete "
            "job/food-master-schema-init --timeout=240s\n"
            "if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }",
            content,
        )
        self.assertGreaterEqual(
            content.count("if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }"),
            10,
        )

    def test_docker_preflight_prevents_proxy_and_tls_bypasses(self):
        script = (
            REPO_ROOT / "03_devops/scripts/check-docker-environment.ps1"
        ).read_text(encoding="utf-8")
        for required_check in (
            "ProxyEnable",
            "Get-NetTCPConnection",
            "host will use proxy:",
            "docker pull",
            "Docker Registry TLS/proxy check",
            "Docker Desktop Kubernetes is running",
        ):
            self.assertIn(required_check, script)

        runbook = (REPO_ROOT / "03_devops/docker/proxy-and-certificate.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("127.0.0.1:7897", runbook)
        self.assertIn("禁止把 Registry 配置成 insecure", runbook)
        self.assertIn("--kubelet-insecure-tls", runbook)

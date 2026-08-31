<#
Run a repeatable HPA scale-up/scale-down experiment against a deployed cluster.
The script intentionally fails early when Metrics Server is unavailable, because
an HPA result without resource metrics is not valid evidence.
#>
[CmdletBinding()]
param(
    [string]$Namespace = "food-master",
    [string]$Deployment = "food-master-trade",
    [string]$GatewayService = "food-master-nginx",
    [string]$BenchmarkPath = "api/trade/health/live",
    [int]$LocalPort = 18080,
    [int]$LoadSeconds = 120,
    [int]$CooldownSeconds = 150,
    [int]$RequestsPerRun = 300,
    [int]$Concurrency = 30,
    [string]$Output = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$resultDir = Join-Path $repoRoot "04_tests\performance\results"
if ([string]::IsNullOrWhiteSpace($Output)) {
    $Output = Join-Path $resultDir "hpa-$timestamp.md"
} elseif (-not [IO.Path]::IsPathRooted($Output)) {
    $Output = Join-Path $repoRoot $Output
}
$Output = [IO.Path]::GetFullPath($Output)
New-Item -ItemType Directory -Force -Path (Split-Path $Output) | Out-Null

function Add-Log([string]$Text) {
    Add-Content -Path $Output -Value $Text -Encoding utf8
}

function Invoke-Kubectl([string]$Label, [string[]]$Arguments) {
    Add-Log "`n## $Label`n`nkubectl $($Arguments -join ' ')`n"
    $result = (& kubectl @Arguments 2>&1 | Out-String).TrimEnd()
    Add-Log ('```text' + "`n" + $result + "`n" + '```')
    if ($LASTEXITCODE -ne 0) {
        throw "kubectl failed for '$Label' (exit code $LASTEXITCODE)."
    }
    return $result
}

Add-Log "# HPA experiment record`n`n- Time: $(Get-Date -Format o)`n- Namespace: $Namespace`n- Deployment: $Deployment`n- Load endpoint: /$BenchmarkPath`n- Load duration: $LoadSeconds seconds`n- Cooldown: $CooldownSeconds seconds"

Invoke-Kubectl "cluster access" @("version", "--request-timeout=5s") | Out-Null
try {
    Invoke-Kubectl "metrics-server availability" @("get", "--raw=/apis/metrics.k8s.io/v1beta1") | Out-Null
} catch {
    Add-Log "`n> Metrics Server is unavailable. Install or enable it before retrying.`n"
    throw
}

Invoke-Kubectl "initial HPA and pods" @("-n", $Namespace, "get", "hpa,pods", "-o", "wide") | Out-Null
Invoke-Kubectl "initial metrics" @("-n", $Namespace, "top", "pods") | Out-Null

$portForwardOut = Join-Path (Split-Path $Output) "hpa-$timestamp-port-forward.log"
$portForwardErr = "$portForwardOut.err"
$watchOut = Join-Path (Split-Path $Output) "hpa-$timestamp-watch.log"
$watchErr = "$watchOut.err"
$portForward = $null
$watch = $null
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }
$benchmark = Join-Path $repoRoot "04_tests\performance\benchmark.py"

try {
    $portForward = Start-Process -FilePath "kubectl" -ArgumentList @(
        "-n", $Namespace, "port-forward", "service/$GatewayService", "$LocalPort`:80"
    ) -RedirectStandardOutput $portForwardOut -RedirectStandardError $portForwardErr -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 3
    if ($portForward.HasExited) { throw "kubectl port-forward exited before the load test started." }

    $watch = Start-Process -FilePath "kubectl" -ArgumentList @(
        "-n", $Namespace, "get", "hpa/$Deployment", "--watch", "--output=wide"
    ) -RedirectStandardOutput $watchOut -RedirectStandardError $watchErr -PassThru -WindowStyle Hidden

    Add-Log "`n## sustained load`n`nThe benchmark runs repeatedly for $LoadSeconds seconds with concurrency=$Concurrency.`n"
    $loadUntil = [DateTime]::UtcNow.AddSeconds($LoadSeconds)
    $run = 0
    while ([DateTime]::UtcNow -lt $loadUntil) {
        $run++
        $benchmarkOutput = Join-Path (Split-Path $Output) "hpa-$timestamp-load-$run.json"
        & $python $benchmark --label "hpa-load-$run" --target "http://127.0.0.1:$LocalPort" --path $BenchmarkPath --requests $RequestsPerRun --concurrency $Concurrency --runs 1 --timeout 3 --output $benchmarkOutput 2>&1 | Tee-Object -FilePath "$benchmarkOutput.log" -Append
        if ($LASTEXITCODE -ne 0) { throw "benchmark failed on run $run (exit code $LASTEXITCODE)." }
    }

    Add-Log "`n## HPA state after load`n"
    Invoke-Kubectl "HPA after load" @("-n", $Namespace, "get", "hpa/$Deployment", "-o", "wide") | Out-Null
    Invoke-Kubectl "pods after load" @("-n", $Namespace, "get", "pods", "-l", "app.kubernetes.io/name=food-master-trade", "-o", "wide") | Out-Null
    Invoke-Kubectl "metrics after load" @("-n", $Namespace, "top", "pods", "-l", "app.kubernetes.io/name=food-master-trade") | Out-Null

    Add-Log "`n## cooldown`n`nWaiting $CooldownSeconds seconds for scale-down stabilization.`n"
    Start-Sleep -Seconds $CooldownSeconds
    Invoke-Kubectl "HPA after cooldown" @("-n", $Namespace, "get", "hpa/$Deployment", "-o", "wide") | Out-Null
    Invoke-Kubectl "pods after cooldown" @("-n", $Namespace, "get", "pods", "-l", "app.kubernetes.io/name=food-master-trade", "-o", "wide") | Out-Null
} finally {
    if ($watch -and -not $watch.HasExited) { Stop-Process -Id $watch.Id -Force }
    if ($portForward -and -not $portForward.HasExited) { Stop-Process -Id $portForward.Id -Force }
    if (Test-Path $watchOut) {
        Add-Log ("`n## HPA watch output`n`n" + '```text' + "`n" + (Get-Content $watchOut -Raw) + '```')
    }
    if (Test-Path $portForwardErr) {
        Add-Log ("`n## port-forward stderr`n`n" + '```text' + "`n" + (Get-Content $portForwardErr -Raw) + '```')
    }
}

Add-Log "`n## acceptance`n`nExpected: replicas increase above 1 during sustained load and return to 1 after cooldown; record the observed values in the submission report."
Write-Output "HPA experiment record: $Output"

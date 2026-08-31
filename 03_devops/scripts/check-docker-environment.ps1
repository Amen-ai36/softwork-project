[CmdletBinding()]
param(
    [string]$ProxyHost = "127.0.0.1",
    [ValidateRange(1, 65535)]
    [int]$ProxyPort = 7897,
    [string]$ProbeImage = "docker/desktop-storage-provisioner:v4.0",
    [switch]$SkipRegistryCheck,
    [switch]$RequireKubernetes
)

$ErrorActionPreference = "Stop"

function Assert-NativeSuccess {
    param([string]$Operation)

    if ($LASTEXITCODE -ne 0) {
        throw "$Operation failed with exit code $LASTEXITCODE."
    }
}

$ExpectedProxy = "$ProxyHost`:$ProxyPort"
$InternetSettings = Get-ItemProperty `
    -LiteralPath "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"

if ([int]$InternetSettings.ProxyEnable -ne 1) {
    throw "Windows system proxy is disabled. Start Clash Verge and enable System Proxy."
}
if ([string]$InternetSettings.ProxyServer -notmatch [regex]::Escape($ExpectedProxy)) {
    throw "Windows proxy '$($InternetSettings.ProxyServer)' does not include $ExpectedProxy."
}

$Listener = Get-NetTCPConnection -State Listen -LocalPort $ProxyPort `
    -ErrorAction SilentlyContinue
if (-not $Listener) {
    throw "No process is listening on proxy port $ProxyPort. Start Clash Verge first."
}
Write-Output "[OK] Windows proxy: $ExpectedProxy"

$DockerVersion = docker version --format '{{.Server.Version}}'
Assert-NativeSuccess "Docker Engine check"
Write-Output "[OK] Docker Engine: $DockerVersion"

$ProxyLog = Join-Path $env:LOCALAPPDATA "Docker\log\host\httpproxy.log"
if (-not (Test-Path -LiteralPath $ProxyLog)) {
    throw "Docker Desktop proxy log was not found: $ProxyLog"
}
$LatestProxyLine = Select-String -LiteralPath $ProxyLog `
    -Pattern "host will use proxy:" | Select-Object -Last 1
if (-not $LatestProxyLine -or
    $LatestProxyLine.Line -notmatch "static system" -or
    $LatestProxyLine.Line -notmatch [regex]::Escape($ExpectedProxy)) {
    throw "Docker Desktop is not using the expected static system proxy. Restart Docker Desktop."
}
Write-Output "[OK] Docker Desktop uses the static system proxy."

if (-not $SkipRegistryCheck) {
    docker pull $ProbeImage | Out-Null
    Assert-NativeSuccess "Docker Registry TLS/proxy check"
    Write-Output "[OK] Docker Registry TLS/proxy check: $ProbeImage"
}

if ($RequireKubernetes) {
    $KubernetesStatus = docker desktop kubernetes status 2>&1
    Assert-NativeSuccess "Docker Desktop Kubernetes status"
    if (($KubernetesStatus -join "`n") -notmatch "State:\s+running") {
        throw "Docker Desktop Kubernetes is not running."
    }
    Write-Output "[OK] Docker Desktop Kubernetes is running."
}

Write-Output "Docker environment preflight passed."

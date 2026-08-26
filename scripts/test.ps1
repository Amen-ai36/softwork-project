param(
    [string]$Python = "python",
    [switch]$RefreshDependencies
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    & $Python -m venv (Join-Path $ProjectRoot ".venv")
    $RefreshDependencies = $true
}

if ($RefreshDependencies) {
    & $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Push-Location $ProjectRoot
try {
    & $VenvPython test\run_tests.py
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}

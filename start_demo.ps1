# ======================================================================
# start_demo.ps1 - PayPilot AI 2.0 Hackathon Demo & Test Launcher
# ======================================================================

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " PAYPILOT AI 2.0 - HACKATHON DEMO LAUNCHER                            " -ForegroundColor Cyan
Write-Host " Built by PayPilot AI Team (Akashdeep, Jaskaran, Suryansh)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] Running automated scenario and guardrail tests..." -ForegroundColor Yellow
$testScript = Join-Path $scriptDir "tests\run_tests.ps1"
& powershell -ExecutionPolicy Bypass -File $testScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Test suite failed. Please review errors." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n[2/2] Opening Interactive PayPilot AI Web Demo in your browser..." -ForegroundColor Yellow
$htmlPath = Join-Path $scriptDir "frontend\index.html"
Start-Process $htmlPath

Write-Host "`n[SUCCESS] Demo launched in your default browser!" -ForegroundColor Green
Write-Host "You can test the $150 College Dorm scenario, Budget Guard, and PayPal Sandbox flow.`n" -ForegroundColor Green

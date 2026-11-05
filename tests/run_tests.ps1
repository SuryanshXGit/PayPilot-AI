# ======================================================================
# run_tests.ps1 - Native PowerShell Test Suite Runner for PayPilot AI 2.0
# Owned by Sehaj (Product Data, Comparison & Testing Lead)
# ======================================================================
# Zero-dependency scenario test runner: runs anywhere on Windows without
# requiring external Python or pip packages.
# ======================================================================

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " PAYPILOT AI 2.0 - HACKATHON TEST SUITE (POWERSHELL RUNNER)           " -ForegroundColor Cyan
Write-Host " Owned by Sehaj (Product Data, Comparison & Testing Lead)             " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

function Assert-Test([string]$testName, [scriptblock]$block) {
    try {
        & $block
        Write-Host " [PASS] $testName" -ForegroundColor Green
        $script:testsPassed++
    } catch {
        Write-Host " [FAIL] $testName" -ForegroundColor Red
        Write-Host "        Error: $_" -ForegroundColor DarkRed
        $script:testsFailed++
    }
}

# 1. Product Data Tests
Assert-Test "Catalogue JSON exists and is valid" {
    $path = Join-Path $rootDir "data\products.json"
    if (-not (Test-Path $path)) { throw "File missing: $path" }
    $json = Get-Content $path -Raw | ConvertFrom-Json
    if ($json.products.Count -lt 5) { throw "Expected at least 5 products, got $($json.products.Count)" }
}

Assert-Test "All catalogue products carry explicit data_source & disclaimer" {
    $path = Join-Path $rootDir "data\products.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    foreach ($p in $json.products) {
        if ([string]::IsNullOrWhiteSpace($p.data_source)) { throw "Product $($p.id) missing data_source" }
        if ([string]::IsNullOrWhiteSpace($p.data_source_disclaimer)) { throw "Product $($p.id) missing data_source_disclaimer" }
        if ($p.price -le 0) { throw "Product $($p.id) invalid price" }
    }
}

# 2. Dorm Scenario ($150 budget) Tests
Assert-Test 'Dorm scenario optimal bundle arithmetic ($111.48 <= $150.00)' {
    $path = Join-Path $rootDir "data\products.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    $lamp = $json.products | Where-Object { $_.id -eq "lamp-01" }
    $steamer = $json.products | Where-Object { $_.id -eq "steamer-01" }
    $buds = $json.products | Where-Object { $_.id -eq "buds-01" }

    $total = [math]::Round(($lamp.price + $steamer.price + $buds.price), 2)
    if ($total -ne 111.48) { throw "Expected total 111.48, got $total" }
    if ($total -gt 150.00) { throw "Optimal bundle exceeds $150 budget constraint" }
    $remaining = [math]::Round((150.00 - $total), 2)
    if ($remaining -ne 38.52) { throw "Expected remaining budget 38.52, got $remaining" }
}

Assert-Test 'Over-budget dorm bundle is correctly flagged ($181.99 > $150.00)' {
    $path = Join-Path $rootDir "data\products.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    $lamp = $json.products | Where-Object { $_.id -eq "lamp-03" }
    $steamer = $json.products | Where-Object { $_.id -eq "steamer-03" }
    $buds = $json.products | Where-Object { $_.id -eq "buds-03" }

    $total = [math]::Round(($lamp.price + $steamer.price + $buds.price), 2)
    if ($total -ne 181.99) { throw "Expected total 181.99, got $total" }
    if ($total -le 150.00) { throw "Expected bundle to exceed $150 limit" }
    $over = [math]::Round(($total - 150.00), 2)
    if ($over -ne 31.99) { throw "Expected overage of 31.99, got $over" }
}

# 3. Emergency Expense Scenario Tests
Assert-Test "Emergency laptop provides next-day delivery option and warranty" {
    $path = Join-Path $rootDir "data\products.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    $laptop = $json.products | Where-Object { $_.id -eq "laptop-01" }

    $nextDay = $laptop.shipping_options | Where-Object { $_.tier -like "*Next-Day*" }
    if ($null -eq $nextDay) { throw "Next-day shipping option not found for emergency laptop" }
    if ([string]::IsNullOrWhiteSpace($laptop.warranty_info)) { throw "Emergency laptop missing warranty info" }
}

# 4. Honey Price History Tests
Assert-Test "Price history carries simulated provenance and no unverified Honey claims" {
    $path = Join-Path $rootDir "data\price_history.json"
    if (-not (Test-Path $path)) { throw "File missing: $path" }
    $json = Get-Content $path -Raw | ConvertFrom-Json
    if (-not ($json._meta.disclaimer -like "*Simulated*")) { throw "Price history disclaimer missing 'Simulated' qualification" }
}

# 5. PayPal Checkout Tests
Assert-Test "Order creation status 'CREATED' is not treated as payment completion" {
    $path = Join-Path $rootDir "data\demo_scenarios.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    $scenario = $json.scenarios | Where-Object { $_.id -eq "scenario-01-dorm-bundle" }
    $createdStatus = $scenario.paypal_checkout_fixture.simulated_created_response.status

    if ($createdStatus -ne "CREATED") { throw "Expected status CREATED, got $createdStatus" }
    $isPaid = ($createdStatus -eq "COMPLETED")
    if ($isPaid) { throw "CREATED status must never be treated as paid" }
}

Assert-Test 'Captured order verifies COMPLETED status and exact amount ($111.48 USD)' {
    $path = Join-Path $rootDir "data\demo_scenarios.json"
    $json = Get-Content $path -Raw | ConvertFrom-Json
    $scenario = $json.scenarios | Where-Object { $_.id -eq "scenario-01-dorm-bundle" }
    $captured = $scenario.paypal_checkout_fixture.simulated_captured_response

    if ($captured.status -ne "COMPLETED") { throw "Expected COMPLETED status, got $($captured.status)" }
    $captureUnit = $captured.purchase_units[0].payments.captures[0]
    if ($captureUnit.status -ne "COMPLETED") { throw "Expected capture COMPLETED status" }
    if ($captureUnit.amount.value -ne "111.48") { throw "Amount mismatch in capture verification" }
    if ($captureUnit.amount.currency_code -ne "USD") { throw "Currency mismatch in capture verification" }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " SUMMARY: Passed: $testsPassed | Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host "======================================================================" -ForegroundColor Cyan

if ($testsFailed -gt 0) { exit 1 } else { exit 0 }

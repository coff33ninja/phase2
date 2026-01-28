# Quick Chat Test Script
# Tests the Nexus chat API integration with Sage

param(
    [string]$Message = "What is my current system status?"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Nexus Chat API Test ===" -ForegroundColor Cyan
Write-Host ""

# Check if Nexus is running
Write-Host "1. Checking Nexus health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
    Write-Host "   ✓ Nexus is running" -ForegroundColor Green
    Write-Host "   Components:" -ForegroundColor Gray
    Write-Host "     - Sentinel: $($health.components.sentinel)" -ForegroundColor Gray
    Write-Host "     - Oracle: $($health.components.oracle)" -ForegroundColor Gray
    Write-Host "     - Sage: $($health.components.sage)" -ForegroundColor Gray
    Write-Host "     - Guardian: $($health.components.guardian)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Nexus is not running!" -ForegroundColor Red
    Write-Host "   Run: .\start-all.ps1 -All" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2. Testing chat API..." -ForegroundColor Yellow
Write-Host "   Message: '$Message'" -ForegroundColor Gray

try {
    $body = @{
        message = $Message
        context = @{}
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/chat/message" `
        -Method Post `
        -Body $body `
        -ContentType "application/json" `
        -TimeoutSec 30

    Write-Host "   ✓ Chat API responded" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Sage Response ===" -ForegroundColor Cyan
    Write-Host $response.response -ForegroundColor White
    Write-Host ""
    Write-Host "Confidence: $($response.confidence)" -ForegroundColor Gray
    
} catch {
    Write-Host "   ✗ Chat API failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard: http://localhost:8001" -ForegroundColor Cyan
Write-Host "API Docs:  http://localhost:8001/docs" -ForegroundColor Cyan

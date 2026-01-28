# AIDA64 Integration Setup Script
# This script helps configure AIDA64 for use with Sentinel

Write-Host "=== AIDA64 Integration Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if AIDA64 is installed
$aida64Paths = @(
    "C:\Program Files\AIDA64\aida64.exe",
    "C:\Program Files (x86)\AIDA64\aida64.exe",
    "$env:ProgramFiles\AIDA64\aida64.exe",
    "${env:ProgramFiles(x86)}\AIDA64\aida64.exe"
)

$aida64Found = $false
$aida64Path = $null

foreach ($path in $aida64Paths) {
    if (Test-Path $path) {
        $aida64Found = $true
        $aida64Path = $path
        break
    }
}

if ($aida64Found) {
    Write-Host "✓ AIDA64 found at: $aida64Path" -ForegroundColor Green
} else {
    Write-Host "✗ AIDA64 not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install AIDA64 Extreme from: https://www.aida64.com/" -ForegroundColor Yellow
    Write-Host "Cost: $39.95 (one-time purchase, 3 PCs)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Free alternatives:" -ForegroundColor Cyan
    Write-Host "  - HWiNFO64: https://www.hwinfo.com/" -ForegroundColor Cyan
    Write-Host "  - LibreHardwareMonitor: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "=== Configuration Options ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Shared Memory (Recommended - Faster)" -ForegroundColor Green
Write-Host "   - AIDA64 must be running"
Write-Host "   - Enable in: File → Preferences → External Applications → Enable shared memory"
Write-Host "   - Check all sensor categories (Temperatures, Voltages, Fans, Power)"
Write-Host ""
Write-Host "2. XML Report File (Alternative)" -ForegroundColor Yellow
Write-Host "   - Configure automatic report generation"
Write-Host "   - File → Preferences → Report → Automatic report generation"
Write-Host "   - Set interval: 30 seconds"
Write-Host "   - Output path: C:\Temp\aida64_report.xml"
Write-Host "   - Format: XML"
Write-Host ""

$choice = Read-Host "Choose method (1 for Shared Memory, 2 for XML Report)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Configuring for Shared Memory..." -ForegroundColor Cyan
    
    # Update .env file
    $envPath = Join-Path $PSScriptRoot ".env"
    
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        
        # Update or add AIDA64 settings
        if ($envContent -match "ENABLE_AIDA64=") {
            $envContent = $envContent -replace "ENABLE_AIDA64=.*", "ENABLE_AIDA64=true"
        } else {
            $envContent += "`nENABLE_AIDA64=true"
        }
        
        if ($envContent -match "AIDA64_SHARED_MEMORY=") {
            $envContent = $envContent -replace "AIDA64_SHARED_MEMORY=.*", "AIDA64_SHARED_MEMORY=true"
        } else {
            $envContent += "`nAIDA64_SHARED_MEMORY=true"
        }
        
        $envContent | Set-Content $envPath -NoNewline
        
        Write-Host "✓ Updated .env file" -ForegroundColor Green
    } else {
        Write-Host "✗ .env file not found. Please copy .env.example to .env first" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Launch AIDA64" -ForegroundColor White
    Write-Host "2. Go to: File → Preferences → External Applications" -ForegroundColor White
    Write-Host "3. Enable 'Enable shared memory'" -ForegroundColor White
    Write-Host "4. Check all sensor categories:" -ForegroundColor White
    Write-Host "   ✓ Temperatures" -ForegroundColor White
    Write-Host "   ✓ Voltages" -ForegroundColor White
    Write-Host "   ✓ Fans" -ForegroundColor White
    Write-Host "   ✓ Power" -ForegroundColor White
    Write-Host "   ✓ Currents" -ForegroundColor White
    Write-Host "   ✓ Clocks" -ForegroundColor White
    Write-Host "5. Click OK" -ForegroundColor White
    Write-Host "6. Restart Sentinel" -ForegroundColor White
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Configuring for XML Report..." -ForegroundColor Cyan
    
    $reportPath = Read-Host "Enter report path (default: C:\Temp\aida64_report.xml)"
    if ([string]::IsNullOrWhiteSpace($reportPath)) {
        $reportPath = "C:\Temp\aida64_report.xml"
    }
    
    # Create directory if it doesn't exist
    $reportDir = Split-Path $reportPath -Parent
    if (-not (Test-Path $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        Write-Host "✓ Created directory: $reportDir" -ForegroundColor Green
    }
    
    # Update .env file
    $envPath = Join-Path $PSScriptRoot ".env"
    
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        
        # Update or add AIDA64 settings
        if ($envContent -match "ENABLE_AIDA64=") {
            $envContent = $envContent -replace "ENABLE_AIDA64=.*", "ENABLE_AIDA64=true"
        } else {
            $envContent += "`nENABLE_AIDA64=true"
        }
        
        if ($envContent -match "AIDA64_SHARED_MEMORY=") {
            $envContent = $envContent -replace "AIDA64_SHARED_MEMORY=.*", "AIDA64_SHARED_MEMORY=false"
        } else {
            $envContent += "`nAIDA64_SHARED_MEMORY=false"
        }
        
        if ($envContent -match "AIDA64_REPORT_PATH=") {
            $envContent = $envContent -replace "AIDA64_REPORT_PATH=.*", "AIDA64_REPORT_PATH=$reportPath"
        } else {
            $envContent += "`nAIDA64_REPORT_PATH=$reportPath"
        }
        
        $envContent | Set-Content $envPath -NoNewline
        
        Write-Host "✓ Updated .env file" -ForegroundColor Green
    } else {
        Write-Host "✗ .env file not found. Please copy .env.example to .env first" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Launch AIDA64" -ForegroundColor White
    Write-Host "2. Go to: File → Preferences → Report" -ForegroundColor White
    Write-Host "3. Enable 'Automatic report generation'" -ForegroundColor White
    Write-Host "4. Set interval: 30 seconds" -ForegroundColor White
    Write-Host "5. Set output path: $reportPath" -ForegroundColor White
    Write-Host "6. Select format: XML" -ForegroundColor White
    Write-Host "7. Check all sections to include" -ForegroundColor White
    Write-Host "8. Click OK" -ForegroundColor White
    Write-Host "9. Restart Sentinel" -ForegroundColor White
    
} else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "To verify AIDA64 integration:" -ForegroundColor Cyan
Write-Host "  cd sentinel" -ForegroundColor White
Write-Host "  .\.venv\Scripts\python.exe main.py collect" -ForegroundColor White
Write-Host ""
Write-Host "Check for temperature data in the output." -ForegroundColor Cyan
Write-Host ""
